#!/usr/bin/env bash
set -o errexit

python manage.py collectstatic --no-input
python manage.py migrate

python manage.py shell -c "from comptes.models import Utilisateur; from core.models import Eglise; import os; eglise, _ = Eglise.objects.get_or_create(nom='Porte des Brebis', defaults={'actif': True}); u, created = Utilisateur.objects.get_or_create(username=os.environ['DJANGO_SUPERUSER_USERNAME'], defaults={'email': os.environ['DJANGO_SUPERUSER_EMAIL'], 'eglise': eglise, 'role': 'administrateur', 'is_staff': True, 'is_superuser': True, 'is_active': True}); u.eglise = eglise; u.role = 'administrateur'; u.is_staff = True; u.is_superuser = True; u.is_active = True; u.email = os.environ['DJANGO_SUPERUSER_EMAIL']; u.save(); u.set_password(os.environ['DJANGO_SUPERUSER_PASSWORD']) if created else None; u.save(); print('SUPERUSER configure')"
if [ -n "${PDB_IMPORT_B64:-}" ]; then
    echo "IMPORT PRODUCTION : fichier detecte"

    python -c "import os, gzip, base64; open('/tmp/pdb_import.json','wb').write(gzip.decompress(base64.b64decode(os.environ['PDB_IMPORT_B64'])))"

    python manage.py shell -c "from membres.models import Membre; print('Membres existants eglise 1 :', Membre.objects.filter(eglise_id=1).count())"

    python manage.py shell -c "from membres.models import Membre; import sys; sys.exit(0 if not Membre.objects.filter(eglise_id=1).exists() else 1)" && \
    python manage.py loaddata /tmp/pdb_import.json --database=default

    echo "IMPORT PRODUCTION TERMINE"
    rm -f /tmp/pdb_import.json
else
    echo "Aucun import production demande"
fi