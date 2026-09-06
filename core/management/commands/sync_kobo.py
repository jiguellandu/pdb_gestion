import os
import unicodedata
import requests
import psycopg2
from psycopg2.extras import execute_values
from django.core.management.base import BaseCommand
from django.conf import settings

KOBO_TOKEN = os.getenv("KOBO_API_TOKEN")
KOBO_BASE_URL = os.getenv("KOBO_BASE_URL", "https://kf.kobotoolbox.org")
HEADERS = {"Authorization": f"Token {KOBO_TOKEN}"}

FORM_UIDS = {
    "achats": "aAZBFgdV8ejpbZvo4YT5XK",
    "finances": "aHokoQNBn9oiBTsAskCF8G",
    "depenses": "aMG6WUqr7zDgnKtErjEKZi",
    "membres": "aCmNrAiS5dRKsa3hA2iYyJ",
    "nouveaux_membres": "aGqbtmufrz4AD6PWVMUwVf",
    "inventaire": "akHnZM9JgpYCWDV9mDSR8n",
    "suivi_activites": "aLXFVRYKf7vEbFSVxX5b3o",
    "evaluations_suivi": "a9KRLLhPBedoj4zT9ab9bi",
    "renseignements_culte": "aDfga6GxN76aQ5b8c9nJnx",
    "preuves_paiement": "aK3VGU6RB2BQxqDwAb99pF",
}


def normaliser(texte):
    texte = (texte or "").strip()
    texte = unicodedata.normalize("NFKD", texte)
    texte = "".join(c for c in texte if not unicodedata.combining(c))
    return texte.lower()


def get_champ(soumission, *noms_possibles):
    cles_dispo = {cle.split("/")[-1].lower(): cle for cle in soumission.keys()}
    for nom in noms_possibles:
        cle_reelle = cles_dispo.get(nom.lower())
        if cle_reelle and soumission.get(cle_reelle):
            return soumission[cle_reelle]
    return ""


def get_submissions(form_uid):
    url = f"{KOBO_BASE_URL}/api/v2/assets/{form_uid}/data.json"
    results = []
    while url:
        resp = requests.get(url, headers=HEADERS, timeout=120)
        resp.raise_for_status()
        payload = resp.json()
        results.extend(payload.get("results", []))
        url = payload.get("next")
    return results


def get_connection():
    db = settings.DATABASES["default"]
    return psycopg2.connect(
        host=db["HOST"], port=db["PORT"], dbname=db["NAME"],
        user=db["USER"], password=db["PASSWORD"],
    )


def get_lookup_map(cur, table, key_col="nom"):
    cur.execute(f"SELECT id, {key_col} FROM {table}")
    return {normaliser(nom): id_ for id_, nom in cur.fetchall()}


def deja_synchronise(cur, table, kobo_uuid):
    cur.execute(f"SELECT 1 FROM {table} WHERE kobo_uuid = %s", (kobo_uuid,))
    return cur.fetchone() is not None


def sync_achats(cur):
    departements = get_lookup_map(cur, "core_departement")
    statuts = get_lookup_map(cur, "core_statut")
    rows = []
    for s in get_submissions(FORM_UIDS["achats"]):
        uuid = s["_uuid"]
        if deja_synchronise(cur, "finance_achat", uuid):
            continue
        rows.append((
            departements.get(normaliser(get_champ(s, "departement"))),
            statuts.get(normaliser(get_champ(s, "statut"))),
            normaliser(get_champ(s, "urgence")) or "faible",
            get_champ(s, "description", "objet", "decription"),
            get_champ(s, "date_demande") or s.get("_submission_time"),
            uuid,
        ))
    if rows:
        execute_values(cur, """
            INSERT INTO finance_achat
                (departement_id, statut_id, urgence, description, date_demande, kobo_uuid)
            VALUES %s
        """, rows)
    return "achats", len(rows)


def sync_finances(cur):
    devises = get_lookup_map(cur, "core_devise", key_col="code")
    rows = []
    for s in get_submissions(FORM_UIDS["finances"]):
        uuid = s["_uuid"]
        if deja_synchronise(cur, "finance_finance", uuid):
            continue
        rows.append((
            normaliser(get_champ(s, "type_trans", "type")) or "offrande",
            devises.get(normaliser(get_champ(s, "devise"))),
            float(get_champ(s, "montant") or 0),
            normaliser(get_champ(s, "nom", "membre", "membre_type")) or "eglise",
            get_champ(s, "date_culte") or s.get("_submission_time"),s.get("_submission_time"),
            uuid,
        ))
    if rows:
        execute_values(cur, """
            INSERT INTO finance_finance
                (type, devise_id, montant, membre_type, date_transaction, date_creation, kobo_uuid)
            VALUES %s
        """, rows)
    return "finances", len(rows)


def sync_depenses(cur):
    departements = get_lookup_map(cur, "core_departement")
    statuts = get_lookup_map(cur, "core_statut")
    devises = get_lookup_map(cur, "core_devise", key_col="code")
    rows = []
    for s in get_submissions(FORM_UIDS["depenses"]):
        uuid = s["_uuid"]
        if deja_synchronise(cur, "finance_depense", uuid):
            continue
        rows.append((
            get_champ(s, "type_depense", "objet") or "non precise",
            devises.get(normaliser(get_champ(s, "devise"))),
            float(get_champ(s, "montant") or 0),
            normaliser(get_champ(s, "mode_paiement")) or "especes",
            statuts.get(normaliser(get_champ(s, "statut"))),
            departements.get(normaliser(get_champ(s, "departement"))),
            get_champ(s, "date_transaction") or s.get("_submission_time"),
            s.get("_submission_time"),
            uuid,
        ))
    if rows:
        execute_values(cur, """
            INSERT INTO finance_depense
                (type_depense, devise_id, montant, mode_paiement, statut_id,
                 departement_id, date_transaction, date_creation, kobo_uuid)
            VALUES %s
        """, rows)
    return "depenses", len(rows)


def sync_membres(cur):
    departements = get_lookup_map(cur, "core_departement")
    rows = []
    for s in get_submissions(FORM_UIDS["membres"]):
        uuid = s["_uuid"]
        if deja_synchronise(cur, "membres_membre", uuid):
            continue
        baptise_txt = normaliser(get_champ(s, "baptise", "bapteme"))
        rows.append((
            get_champ(s, "nom", "nom_complet"),
            (normaliser(get_champ(s, "sexe"))[:1].upper() or "M"),
            normaliser(get_champ(s, "statut_matrimonial")),
            departements.get(normaliser(get_champ(s, "departement"))),
            get_champ(s, "temps_passe_eglise", "temps_passe"),
            baptise_txt in ("oui", "yes", "true", "1"),
            s.get("_submission_time"),
            uuid,
        ))
    if rows:
        execute_values(cur, """
            INSERT INTO membres_membre
                (nom, sexe, statut_matrimonial, departement_id,
                 temps_passe_eglise, baptise, date_creation, kobo_uuid)
            VALUES %s
        """, rows)
    return "membres", len(rows)


def sync_nouveaux_membres(cur):
    rows = []
    for s in get_submissions(FORM_UIDS["nouveaux_membres"]):
        uuid = s["_uuid"]
        if deja_synchronise(cur, "membres_nouveaumembre", uuid):
            continue
        baptise_txt = normaliser(get_champ(s, "baptise", "bapteme"))
        rows.append((
            get_champ(s, "nom", "nom_complet"),
            (normaliser(get_champ(s, "sexe"))[:1].upper() or "M"),
            normaliser(get_champ(s, "statut_matrimonial")),
            baptise_txt in ("oui", "yes", "true", "1"),
            get_champ(s, "jour_visite") or None,
            get_champ(s, "experience"),
            s.get("_submission_time"),
            uuid,
        ))
    if rows:
        execute_values(cur, """
            INSERT INTO membres_nouveaumembre
                (nom, sexe, statut_matrimonial, baptise, jour_visite,
                 experience, date_creation, kobo_uuid)
            VALUES %s
        """, rows)
    return "nouveaux_membres", len(rows)


def sync_inventaire(cur):
    rows = []
    for s in get_submissions(FORM_UIDS["inventaire"]):
        uuid = s["_uuid"]
        if deja_synchronise(cur, "operations_inventaire", uuid):continue
        rows.append((
            get_champ(s, "nom_article", "nom"),
            normaliser(get_champ(s, "type")) or "autre",
            normaliser(get_champ(s, "localisation")) or "salle principale",
            int(get_champ(s, "quantite") or 1),
            uuid,
        ))
    if rows:
        execute_values(cur, """
            INSERT INTO operations_inventaire
                (nom_article, type, localisation, quantite, kobo_uuid)
            VALUES %s
        """, rows)
    return "inventaire", len(rows)


def sync_suivi_activites(cur):
    departements = get_lookup_map(cur, "core_departement")
    statuts = get_lookup_map(cur, "core_statut")
    rows = []
    for s in get_submissions(FORM_UIDS["suivi_activites"]):
        uuid = s["_uuid"]
        if deja_synchronise(cur, "operations_suiviactivite", uuid):
            continue
        rows.append((
            departements.get(normaliser(get_champ(s, "departement"))),
            statuts.get(normaliser(get_champ(s, "statut"))),
            get_champ(s, "description"),
            get_champ(s, "date_activite") or None,
            uuid,
        ))
    if rows:
        execute_values(cur, """
            INSERT INTO operations_suiviactivite
                (departement_id, statut_id, description, date_activite, kobo_uuid)
            VALUES %s
        """, rows)
    return "suivi_activites", len(rows)


def sync_evaluations_suivi(cur):
    departements = get_lookup_map(cur, "core_departement")
    statuts = get_lookup_map(cur, "core_statut")
    rows = []
    for s in get_submissions(FORM_UIDS["evaluations_suivi"]):
        uuid = s["_uuid"]
        if deja_synchronise(cur, "operations_evaluationsuivi", uuid):
            continue
        probleme_txt = normaliser(get_champ(s, "probleme"))
        rows.append((
            departements.get(normaliser(get_champ(s, "departement"))),
            statuts.get(normaliser(get_champ(s, "statut"))),
            normaliser(get_champ(s, "satisfaction")) or "moyenne",
            probleme_txt in ("oui", "yes", "true", "1"),
            get_champ(s, "commentaire"),
            uuid,
        ))
    if rows:
        execute_values(cur, """
            INSERT INTO operations_evaluationsuivi
                (departement_id, statut_id, satisfaction, probleme, commentaire, kobo_uuid)
            VALUES %s
        """, rows)
    return "evaluations_suivi", len(rows)


def sync_renseignements_culte(cur):
    rows = []
    for s in get_submissions(FORM_UIDS["renseignements_culte"]):
        uuid = s["_uuid"]
        if deja_synchronise(cur, "operations_renseignementculte", uuid):
            continue
        rows.append((
            normaliser(get_champ(s, "statut_predicateur")) or "interne",
            normaliser(get_champ(s, "type_culte")) or "dimanche",
            get_champ(s, "nom_predicateur"),
            get_champ(s, "date_culte") or None,
            uuid,
        ))
    if rows:
        execute_values(cur, """
            INSERT INTO operations_renseignementculte
                (statut_predicateur, type_culte, nom_predicateur, date_culte, kobo_uuid)
            VALUES %s
        """, rows)
    return "renseignements_culte", len(rows)


def sync_preuves_paiement(cur):
    departements = get_lookup_map(cur, "core_departement")
    devises = get_lookup_map(cur, "core_devise", key_col="code")
    rows = []
    for s in get_submissions(FORM_UIDS["preuves_paiement"]):
        uuid = s["_uuid"]
        if deja_synchronise(cur, "finance_preuvepaiement", uuid):
            continue
        rows.append((
            departements.get(normaliser(get_champ(s, "departement"))),
            devises.get(normaliser(get_champ(s, "devise"))),
            float(get_champ(s, "montant") or 0) or None,
            normaliser(get_champ(s, "mode_paiement")) or "especes",s.get("_submission_time"),
            uuid,
        ))
    if rows:
        execute_values(cur, """
            INSERT INTO finance_preuvepaiement
                (departement_id, devise_id, montant, mode_paiement, date_creation, kobo_uuid)
            VALUES %s
        """, rows)
    return "preuves_paiement", len(rows)


TOUTES_LES_SYNC = [
    sync_achats, sync_finances, sync_depenses, sync_membres,
    sync_nouveaux_membres, sync_inventaire, sync_suivi_activites,
    sync_evaluations_suivi, sync_renseignements_culte, sync_preuves_paiement,
]


class Command(BaseCommand):
    help = "Synchronise les 10 formulaires KoboToolbox vers PostgreSQL"

    def handle(self, *args, **options):
        resultats = []
        conn = get_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    for fonction in TOUTES_LES_SYNC:
                        nom, nb = fonction(cur)
                        resultats.append((nom, nb))
        finally:
            conn.close()

        for nom, nb in resultats:
            self.stdout.write(f"{nom} : {nb} nouvelle(s) soumission(s)")