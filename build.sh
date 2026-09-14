#!/usr/bin/env bash
set -o errexit

python manage.py collectstatic --no-input
python manage.py migrate

python manage.py shell -c "from comptes.models import Utilisateur; from core.models import Eglise; import os; u, created = Utilisateur.objects.get_or_create(username=os.environ['DJANGO_SUPERUSER_USERNAME'], defaults={'email': os.environ['DJANGO_SUPERUSER_EMAIL'], 'eglise': Eglise.objects.get(id=1), 'role': 'administrateur', 'is_staff': True, 'is_superuser': True, 'is_active': True}); u.set_password(os.environ['DJANGO_SUPERUSER_PASSWORD']); u.save(); print('SUPERUSER configure')"