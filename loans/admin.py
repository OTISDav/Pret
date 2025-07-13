from django.contrib import admin
from .models import DemandePret, TypePret, HistoriqueStatut


@admin.register(DemandePret)
class DemandePretAdmin(admin.ModelAdmin):
    list_display = ('numero_dossier', 'fonctionnaire', 'type_pret', 'montant', 'statut', 'date_soumission')
    list_filter = ('statut', 'type_pret', 'date_soumission')
    search_fields = ('numero_dossier', 'fonctionnaire__email', 'fonctionnaire__cin_number')
    readonly_fields = ('numero_dossier', 'date_soumission')

    fields = ('fonctionnaire', 'type_pret', 'montant', 'duree_remboursement', 'adresse_bien', 'statut')



@admin.register(TypePret)
class TypePretAdmin(admin.ModelAdmin):
    list_display = ('nom', 'description')


@admin.register(HistoriqueStatut)
class HistoriqueStatutAdmin(admin.ModelAdmin):
    list_display = ('demande', 'statut', 'date_modification', 'commentaire')
    list_filter = ('statut', 'date_modification')
