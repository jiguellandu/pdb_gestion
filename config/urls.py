from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('comptes/', include('comptes.urls')),
    path('agenda/', include('agenda.urls')),
    path('membres/', include('membres.urls')),
    path('finance/', include('finance.urls')),
    path('operations/', include('operations.urls')),
    path('core/', include('core.urls')),
    path('', include('dashboard.urls')),
]