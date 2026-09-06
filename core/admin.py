from django.contrib import admin
from .models import Departement, Devise, Statut, PermissionFormulaire, JournalActivite


admin.site.register(Departement)
admin.site.register(Devise)
admin.site.register(Statut)
admin.site.register(PermissionFormulaire)


@admin.register(JournalActivite)
class JournalActiviteAdmin(admin.ModelAdmin):
    list_display = ["date_action", "utilisateur", "action", "modele", "objet_id"]
    list_filter = ["action", "modele"]
    readonly_fields = [f.name for f in JournalActivite._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False