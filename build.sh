#!/usr/bin/env bash
set -o errexit

python manage.py collectstatic --no-input
python manage.py migrate

python manage.py shell -c "from comptes.models import Utilisateur; from core.models import Eglise; import os; eglise, _ = Eglise.objects.get_or_create(nom='Porte des Brebis', defaults={'actif': True}); u, created = Utilisateur.objects.get_or_create(username=os.environ['DJANGO_SUPERUSER_USERNAME'], defaults={'email': os.environ['DJANGO_SUPERUSER_EMAIL'], 'eglise': eglise, 'role': 'administrateur', 'is_staff': True, 'is_superuser': True, 'is_active': True}); u.eglise = eglise; u.role = 'administrateur'; u.is_staff = True; u.is_superuser = True; u.is_active = True; u.email = os.environ['DJANGO_SUPERUSER_EMAIL']; u.save(); u.set_password(os.environ['DJANGO_SUPERUSER_PASSWORD']) if created else None; u.save(); print('SUPERUSER configure')"