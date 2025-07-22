from rest_framework import serializers
from .models import DemandePret, TypePret, HistoriqueStatut



class DemandePretSerializer(serializers.ModelSerializer):
    fonctionnaire_nom = serializers.SerializerMethodField()
    class Meta:
        model = DemandePret
        fields = [
            'id', 'fonctionnaire', 'fonctionnaire_nom','type_pret', 'montant', 'duree_remboursement',
            'adresse_bien', 'statut', 'numero_dossier', 'date_soumission',
            'pieces_jointes'
        ]
        read_only_fields = ['statut', 'numero_dossier', 'date_soumission', 'fonctionnaire']

    def get_fonctionnaire_nom(self, obj):
        return obj.fonctionnaire.last_name if obj.fonctionnaire else None


class DemandePretCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DemandePret
        fields = [
            'type_pret', 'montant', 'duree_remboursement', 'adresse_bien'
        ]


class HistoriqueStatutSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoriqueStatut
        fields = ['id', 'statut', 'commentaire', 'date_modification']
