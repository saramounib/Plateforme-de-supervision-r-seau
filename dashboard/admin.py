from django.contrib import admin
from .models import Agence, Alerte

@admin.register(Agence)
class AgenceAdmin(admin.ModelAdmin):
    list_display = ('nom', 'ville', 'latence', 'perte_paquets', 'bande_passante', 'statut')
    list_filter = ('statut', 'ville')#list_filter permet de filtrer rapidement les agenc
    search_fields = ('nom', 'ville')#search_fields permet de rechercher des agences par nom ou par ville.

@admin.register(Alerte)
class AlerteAdmin(admin.ModelAdmin):
    list_display = ('type_alerte', 'agence', 'severite', 'statut', 'date_creation')
    list_filter = ('statut', 'severite', 'agence')
    search_fields = ('type_alerte', 'agence__nom')