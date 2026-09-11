import unicodedata
import time

import psycopg2
import requests

from psycopg2.extras import execute_values
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from core.models import Eglise, KoboConfiguration, KoboFormulaire


def normaliser(texte):
    texte = (texte or "").strip()
    texte = unicodedata.normalize("NFKD", texte)
    texte = "".join(
        c for c in texte
        if not unicodedata.combining(c)
    )
    return texte.lower()


def get_champ(soumission, *noms_possibles):
    """
    Recherche une valeur dans une soumission Kobo.

    1. Recherche d'abord la clé exacte.
    2. Si elle n'existe pas, recherche par nom court.
    """

    # Recherche exacte
    for nom in noms_possibles:
        if nom in soumission:
            valeur = soumission.get(nom)

            if valeur not in (None, ""):
                return valeur

    # Recherche par nom court
    for nom in noms_possibles:
        nom_court = nom.split("/")[-1].lower()

        for cle, valeur in soumission.items():
            if cle.split("/")[-1].lower() == nom_court:
                if valeur not in (None, ""):
                    return valeur

    return ""


def get_submissions(form_uid, base_url, token):
    """
    Récupère toutes les soumissions Kobo.
    Gère la pagination et les erreurs temporaires.
    """

    url = (
        f"{base_url.rstrip('/')}"
        f"/api/v2/assets/{form_uid}/data.json"
    )

    headers = {
        "Authorization": f"Token {token}"
    }

    results = []

    while url:

        for tentative in range(1, 4):

            try:
                response = requests.get(
                    url,
                    headers=headers,
                    params={"limit": 100},
                    timeout=120,
                )

                response.raise_for_status()
                break

            except requests.exceptions.ConnectionError:

                if tentative == 3:
                    raise

                time.sleep(tentative * 3)

        payload = response.json()

        results.extend(
            payload.get("results", [])
        )

        url = payload.get("next")

    return results


def get_connection():
    db = settings.DATABASES["default"]

    return psycopg2.connect(
        host=db["HOST"],
        port=db["PORT"],
        dbname=db["NAME"],
        user=db["USER"],
        password=db["PASSWORD"],
    )


def table_has_eglise(cur, table):
    cur.execute(
        """
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.columns
            WHERE table_name = %s
            AND column_name = 'eglise_id'
        )
        """,
        (table,),
    )

    return cur.fetchone()[0]


def get_lookup_map(
    cur,
    table,
    key_col="nom",
    eglise_id=None,
):
    if eglise_id is not None and table_has_eglise(
        cur,
        table,
    ):
        cur.execute(
            f"""
            SELECT id, {key_col}
            FROM {table}
            WHERE eglise_id = %s
            """,
            (eglise_id,),
        )

    else:
        cur.execute(
            f"""
            SELECT id, {key_col}
            FROM {table}
            """
        )

    return {
        normaliser(nom): id_
        for id_, nom in cur.fetchall()
    }


def deja_synchronise(
    cur,
    table,
    kobo_uuid,
    eglise_id,
):
    if table_has_eglise(cur, table):

        cur.execute(
            f"""
            SELECT 1
            FROM {table}
            WHERE kobo_uuid = %s
            AND eglise_id = %s
            LIMIT 1
            """,
            (kobo_uuid, eglise_id),
        )

    else:

        cur.execute(
            f"""
            SELECT 1
            FROM {table}
            WHERE kobo_uuid = %s
            LIMIT 1
            """,
            (kobo_uuid,),
        )

    return cur.fetchone() is not None


def sync_achats(
    cur,
    eglise_id,
    form_uids,
    base_url,
    token,
):
    departements = get_lookup_map(
        cur,
        "core_departement",
        eglise_id=eglise_id,
    )

    statuts = get_lookup_map(
        cur,
        "core_statut",
        eglise_id=eglise_id,
    )

    rows = []

    for s in get_submissions(
        form_uids["achats"],
        base_url,
        token,
    ):
        uuid = s.get("_uuid")

        if not uuid:
            continue

        if deja_synchronise(
            cur,
            "finance_achat",
            uuid,
            eglise_id,
        ):
            continue

        rows.append(
            (
                eglise_id,

                departements.get(
                    normaliser(
                        get_champ(
                            s,
                            "departement",
                        )
                    )
                ),

                statuts.get(
                    normaliser(
                        get_champ(
                            s,
                            "statut",
                        )
                    )
                ),

                normaliser(
                    get_champ(
                        s,
                        "urgence",
                    )
                ) or "faible",

                get_champ(
                    s,
                    "description",
                    "objet",
                    "decription",
                ),

                get_champ(
                    s,
                    "date_demande",
                ) or s.get("_submission_time"),

                uuid,
            )
        )

    if rows:
        execute_values(
            cur,
            """
            INSERT INTO finance_achat
            (
                eglise_id,
                departement_id,
                statut_id,
                urgence,
                description,
                date_demande,
                kobo_uuid
            )
            VALUES %s
            """,
            rows,
        )

    return "achats", len(rows)


def sync_finances(
    cur,
    eglise_id,
    form_uids,
    base_url,
    token,
):
    devises = get_lookup_map(
        cur,
        "core_devise",
        key_col="code",
        eglise_id=eglise_id,
    )

    rows = []

    for s in get_submissions(
        form_uids["finances"],
        base_url,
        token,
    ):
        uuid = s.get("_uuid")

        if not uuid:
            continue

        if deja_synchronise(
            cur,
            "finance_finance",
            uuid,
            eglise_id,
        ):
            continue

        rows.append(
            (
                eglise_id,

                normaliser(
                    get_champ(
                        s,
                        "type_trans",
                        "type",
                    )
                ) or "offrande",

                devises.get(
                    normaliser(
                        get_champ(
                            s,
                            "devise",
                        )
                    )
                ),

                float(
                    get_champ(
                        s,
                        "montant",
                    ) or 0
                ),

                normaliser(
                    get_champ(
                        s,
                        "nom",
                        "membre",
                        "membre_type",
                    )
                ) or "eglise",

                get_champ(
                    s,
                    "date_culte",
                ) or s.get("_submission_time"),

                s.get("_submission_time"),

                uuid,
            )
        )

    if rows:
        execute_values(
            cur,
            """
            INSERT INTO finance_finance
            (
                eglise_id,
                type,
                devise_id,
                montant,
                membre_type,
                date_transaction,
                date_creation,
                kobo_uuid
            )
            VALUES %s
            """,
            rows,
        )

    return "finances", len(rows)

def sync_depenses(
    cur,
    eglise_id,
    form_uids,
    base_url,
    token,
):
    departements = get_lookup_map(
        cur,
        "core_departement",
        eglise_id=eglise_id,
    )

    statuts = get_lookup_map(
        cur,
        "core_statut",
        eglise_id=eglise_id,
    )

    devises = get_lookup_map(
        cur,
        "core_devise",
        key_col="code",
        eglise_id=None,
    )

    correspondance_departements = {
        "tech": "technique",
    }

    correspondance_statuts = {
        "valide": "realise",
    }

    rows = []

    for s in get_submissions(
        form_uids["depenses"],
        base_url,
        token,
    ):
        uuid = s.get("_uuid")

        if not uuid:
            continue

        if deja_synchronise(
            cur,
            "finance_depense",
            uuid,
            eglise_id,
        ):
            continue

        departement_kobo = normaliser(
            get_champ(
                s,
                "info_depense/departement",
                "departement",
            )
        )

        departement_nom = correspondance_departements.get(
            departement_kobo,
            departement_kobo,
        )

        departement_id = departements.get(
            normaliser(departement_nom)
        )

        if not departement_id:
            print(
                f"Depense ignorée : département introuvable "
                f"pour l'église {eglise_id} : "
                f"{repr(departement_kobo)}"
            )
            continue

        type_depense = get_champ(
            s,
            "details/type_depense",
            "type_depense",
        )

        if normaliser(type_depense) == "autres":
            type_depense = get_champ(
                s,
                "details/autres_type_depense",
                "autres_type_depense",
            ) or "autres"

        devise_id = devises.get(
            normaliser(
                get_champ(
                    s,
                    "details/devise_depense",
                    "devise",
                )
            )
        )

        statut_kobo = normaliser(
            get_champ(
                s,
                "suivi/statut",
                "statut",
            )
        )

        statut_nom = correspondance_statuts.get(
            statut_kobo,
            statut_kobo,
        )

        statut_id = statuts.get(
            normaliser(statut_nom)
        )

        rows.append(
            (
                eglise_id,
                type_depense or "non precise",
                devise_id,
                float(
                    get_champ(
                        s,
                        "details/montant_depense",
                        "montant",
                    ) or 0
                ),
                normaliser(
                    get_champ(
                        s,
                        "paiement/mode_paiement",
                        "mode_paiement",
                    )
                ) or "especes",
                statut_id,
                departement_id,
                get_champ(
                    s,
                    "info_depense/date_depense",
                    "date_depense",
                ) or s.get("_submission_time"),
                s.get("_submission_time"),
                   uuid,
            )
        )

    if rows:
        execute_values(
            cur,
            """
            INSERT INTO 
finance_depense
            (
                eglise_id,
                type_depense,
                devise_id,
                montant,
                mode_paiement,
                statut_id,
                departement_id,
                date_transaction,
                date_creation,
                kobo_uuid
            )
            VALUES %s
            """,
            rows,
        )

    return "depenses", len(rows)


def sync_membres(
    cur,
    eglise_id,
    form_uids,
    base_url,
    token,
):
    departements = get_lookup_map(
        cur,
        "core_departement",
        eglise_id=eglise_id,
    )

    rows = []

    for s in get_submissions(
        form_uids["membres"],
        base_url,
        token,
    ):
        uuid = s.get("_uuid")

        if not uuid:
            continue

        if deja_synchronise(
            cur,
            "membres_membre",
            uuid,
            eglise_id,
        ):
            continue

        baptise_txt = normaliser(
            get_champ(
                s,
                "baptise",
                "bapteme",
            )
        )

        rows.append(
            (
                eglise_id,

                get_champ(
                    s,
                    "nom",
                    "nom_complet",
                ),

                (
                    normaliser(
                        get_champ(
                            s,
                            "sexe",
                        )
                    )[:1].upper()
                    or "M"
                ),

                normaliser(
                    get_champ(
                        s,
                        "statut_matrimonial",
                    )
                ),

                departements.get(
                    normaliser(
                        get_champ(
                            s,
                            "departement",
                        )
                    )
                ),

                get_champ(
                    s,
                    "temps_passe_eglise",
                    "temps_passe",
                ),

                baptise_txt in (
                    "oui",
                    "yes",
                    "true",
                    "1",
                ),

                s.get("_submission_time"),

                uuid,
            )
        )

    if rows:
        execute_values(
            cur,
            """
            INSERT INTO membres_membre
            (
                eglise_id,
                nom,
                sexe,
                statut_matrimonial,
                departement_id,
                temps_passe_eglise,
                baptise,
                date_creation,
                kobo_uuid
            )
            VALUES %s
            """,
            rows,
        )

    return "membres", len(rows)


def sync_nouveaux_membres(
    cur,
    eglise_id,
    form_uids,
    base_url,
    token,
):
    rows = []

    for s in get_submissions(
        form_uids["nouveaux_membres"],
        base_url,
        token,
    ):
        uuid = s.get("_uuid")

        if not uuid:
            continue

        if deja_synchronise(
            cur,
            "membres_nouveaumembre",
            uuid,
            eglise_id,
        ):
            continue

        baptise_txt = normaliser(
            get_champ(
                s,
                "baptise",
                "bapteme",
            )
        )

        rows.append(
            (
                eglise_id,

                get_champ(
                    s,
                    "nom",
                    "nom_complet",
                ),

                (
                    normaliser(
                        get_champ(
                            s,
                            "sexe",
                        )
                    )[:1].upper()
                    or "M"
                ),

                normaliser(
                    get_champ(
                        s,
                        "statut_matrimonial",
                    )
                ),

                baptise_txt in (
                    "oui",
                    "yes",
                    "true",
                    "1",
                ),

                get_champ(
                    s,
                    "jour_visite",
                ) or None,

                get_champ(
                    s,
                    "experience",
                ),

                s.get("_submission_time"),

                uuid,
            )
        )

    if rows:
        execute_values(
            cur,
            """
            INSERT INTO membres_nouveaumembre
            (
                eglise_id,
                nom,
                sexe,
                statut_matrimonial,
                baptise,
                jour_visite,
                experience,
                date_creation,
                kobo_uuid
            )
            VALUES %s
            """,
            rows,
        )

    return "nouveaux_membres", len(rows)


def sync_inventaire(
    cur,
    eglise_id,
    form_uids,
    base_url,
    token,
):
    rows = []

    for s in get_submissions(
        form_uids["inventaire"],
        base_url,
        token,
    ):
        uuid = s.get("_uuid")

        if not uuid:
            continue

        if deja_synchronise(
            cur,
            "operations_inventaire",
            uuid,
            eglise_id,
        ):
            continue

        rows.append(
            (
                eglise_id,

                get_champ(
                    s,
                    "nom_article",
                    "nom",
                ),

                normaliser(
                    get_champ(
                        s,
                        "type",
                    )
                ) or "autre",

                normaliser(
                    get_champ(
                        s,
                        "localisation",
                    )
                ) or "salle principale",

                int(
                    get_champ(
                        s,
                        "quantite",
                    ) or 1
                ),

                uuid,
            )
        )

    if rows:
        execute_values(
            cur,
            """
            INSERT INTO operations_inventaire
            (
                eglise_id,
                nom_article,
                type,
                localisation,
                quantite,
                kobo_uuid
            )
            VALUES %s
            """,
            rows,
        )

    return "inventaire", len(rows)


def sync_suivi_activites(
    cur,
    eglise_id,
    form_uids,
    base_url,
    token,
):
    departements = get_lookup_map(
        cur,
        "core_departement",
        eglise_id=eglise_id,
    )

    statuts = get_lookup_map(
        cur,
        "core_statut",
        eglise_id=eglise_id,
    )

    rows = []

    for s in get_submissions(
        form_uids["suivi_activites"],
        base_url,
        token,
    ):
        uuid = s.get("_uuid")

        if not uuid:
            continue

        if deja_synchronise(
            cur,
            "operations_suiviactivite",
            uuid,
            eglise_id,
        ):
            continue

        rows.append(
            (
                eglise_id,

                departements.get(
                    normaliser(
                        get_champ(
                            s,
                            "departement",
                        )
                    )
                ),

                statuts.get(
                    normaliser(
                        get_champ(
                            s,
                            "statut",
                        )
                    )
                ),

                get_champ(
                    s,
                    "description",
                ),

                get_champ(
                    s,
                    "date_activite",
                ) or None,

                uuid,
            )
        )

    if rows:
        execute_values(
            cur,
            """
            INSERT INTO operations_suiviactivite
            (
                eglise_id,
                departement_id,
                statut_id,
                description,
                date_activite,
                kobo_uuid
            )
            VALUES %s
            """,
            rows,
        )

    return "suivi_activites", len(rows)


def sync_evaluations_suivi(
    cur,
    eglise_id,
    form_uids,
    base_url,
    token,
):
    departements = get_lookup_map(
        cur,
        "core_departement",
        eglise_id=eglise_id,
    )

    statuts = get_lookup_map(
        cur,
        "core_statut",
        eglise_id=eglise_id,
    )

    rows = []

    for s in get_submissions(
        form_uids["evaluations_suivi"],
        base_url,
        token,
    ):
        uuid = s.get("_uuid")

        if not uuid:
            continue

        if deja_synchronise(
            cur,
            "operations_evaluationsuivi",
            uuid,
            eglise_id,
        ):
            continue

        probleme_txt = normaliser(
            get_champ(
                s,
                "probleme",
            )
        )

        rows.append(
            (
                eglise_id,

                departements.get(
                    normaliser(
                        get_champ(
                            s,
                            "departement",
                        )
                    )
                ),

                statuts.get(
                    normaliser(
                        get_champ(
                            s,
                            "statut",
                        )
                    )
                ),

                normaliser(
                    get_champ(
                        s,
                        "satisfaction",
                    )
                ) or "moyenne",

                probleme_txt in (
                    "oui",
                    "yes",
                    "true",
                    "1",
                ),

                get_champ(
                    s,
                    "commentaire",
                ),

                uuid,
            )
        )

    if rows:
        execute_values(
            cur,
            """
            INSERT INTO operations_evaluationsuivi
            (
                eglise_id,
                departement_id,
                statut_id,
                satisfaction,
                probleme,
                commentaire,
                kobo_uuid
            )
            VALUES %s
            """,
            rows,
        )

    return "evaluations_suivi", len(rows)


def sync_renseignements_culte(
    cur,
    eglise_id,
    form_uids,
    base_url,
    token,
):
    rows = []

    for s in get_submissions(
        form_uids["renseignements_culte"],
        base_url,
        token,
    ):
        uuid = s.get("_uuid")

        if not uuid:
            continue

        if deja_synchronise(
            cur,
            "operations_renseignementculte",
            uuid,
            eglise_id,
        ):
            continue

        rows.append(
            (
                eglise_id,

                normaliser(
                    get_champ(
                        s,
                        "statut_predicateur",
                    )
                ) or "interne",

                normaliser(
                    get_champ(
                        s,
                        "type_culte",
                    )
                ) or "dimanche",

                get_champ(
                    s,
                    "nom_predicateur",
                ),

                get_champ(
                    s,
                    "date_culte",
                ) or None,

                uuid,
            )
        )

    if rows:
        execute_values(
            cur,
            """
            INSERT INTO operations_renseignementculte
            (
                eglise_id,
                statut_predicateur,
                type_culte,
                nom_predicateur,
                date_culte,
                kobo_uuid
            )
            VALUES %s
            """,
            rows,
        )

    return "renseignements_culte", len(rows)


def sync_preuves_paiement(
    cur,
    eglise_id,
    form_uids,
    base_url,
    token,
):
    departements = get_lookup_map(
        cur,
        "core_departement",
        eglise_id=eglise_id,
    )

    devises = get_lookup_map(
        cur,
        "core_devise",
        key_col="code",
        eglise_id=eglise_id,
    )

    rows = []

    for s in get_submissions(
        form_uids["preuves_paiement"],
        base_url,
        token,
    ):
        uuid = s.get("_uuid")

        if not uuid:
            continue

        if deja_synchronise(
            cur,
            "finance_preuvepaiement",
            uuid,
            eglise_id,
        ):
            continue

        rows.append(
            (
                eglise_id,

                departements.get(
                    normaliser(
                        get_champ(
                            s,
                            "departement",
                        )
                    )
                ),

                devises.get(
                    normaliser(
                        get_champ(
                            s,
                            "devise",
                        )
                    )
                ),

                float(
                    get_champ(
                        s,
                        "montant",
                    ) or 0
                ) or None,

                normaliser(
                    get_champ(
                        s,
                        "mode_paiement",
                    )
                ) or "especes",

                s.get("_submission_time"),

                uuid,
            )
        )

    if rows:
        execute_values(
            cur,
            """
            INSERT INTO finance_preuvepaiement
            (
                eglise_id,
                departement_id,
                devise_id,
                montant,
                mode_paiement,
                date_creation,
                kobo_uuid
            )
            VALUES %s
            """,
            rows,
        )

    return "preuves_paiement", len(rows)


TOUTES_LES_SYNC = [
    sync_achats,
    sync_finances,
    sync_depenses,
    sync_membres,
    sync_nouveaux_membres,
    sync_inventaire,
    sync_suivi_activites,
    sync_evaluations_suivi,
    sync_renseignements_culte,
    sync_preuves_paiement,
]


class Command(BaseCommand):

    help = (
        "Synchronise les 10 formulaires KoboToolbox "
        "d'une église vers PostgreSQL"
    )

    def add_arguments(self, parser):

        parser.add_argument(
            "--eglise",
            type=int,
            required=True,
            help="ID de l'église à synchroniser",
        )

    def handle(self, *args, **options):

        eglise_id = options["eglise"]

        try:

            eglise = Eglise.objects.get(
                id=eglise_id
            )

        except Eglise.DoesNotExist:

            raise CommandError(
                f"L'église avec l'ID {eglise_id} "
                f"n'existe pas."
            )

        try:

            configuration = KoboConfiguration.objects.get(
                eglise=eglise,
                actif=True,
            )

        except KoboConfiguration.DoesNotExist:

            raise CommandError(
                f"Aucune configuration Kobo active "
                f"pour l'église « {eglise.nom} »."
            )

        formulaires = KoboFormulaire.objects.filter(
            eglise=eglise,
            actif=True,
        )

        form_uids = {
            formulaire.nom: formulaire.uid
            for formulaire in formulaires
        }

        noms_requis = {
            "achats",
            "finances",
            "depenses",
            "membres",
            "nouveaux_membres",
            "inventaire",
            "suivi_activites",
            "evaluations_suivi",
            "renseignements_culte",
            "preuves_paiement",
        }

        formulaires_manquants = (
            noms_requis - set(form_uids.keys())
        )

        if formulaires_manquants:

            raise CommandError(
                "Formulaires Kobo manquants pour "
                f"« {eglise.nom} » : "
                + ", ".join(
                    sorted(formulaires_manquants)
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Synchronisation Kobo : {eglise.nom}"
            )
        )

        self.stdout.write(
            f"URL Kobo : {configuration.base_url}"
        )

        resultats = []

        conn = get_connection()

        try:

            with conn:

                with conn.cursor() as cur:

                    for fonction in TOUTES_LES_SYNC:

                        nom, nb = fonction(
                            cur,
                            eglise_id,
                            form_uids,
                            configuration.base_url,
                            configuration.api_token,
                        )

                        resultats.append(
                            (nom, nb)
                        )

        except requests.RequestException as exc:

            raise CommandError(
                f"Erreur de connexion à KoboToolbox : {exc}"
            )

        finally:

            conn.close()

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                "Synchronisation terminée."
            )
        )

        for nom, nb in resultats:

            self.stdout.write(
                f"{nom} : {nb} nouvelle(s) soumission(s)"
            )