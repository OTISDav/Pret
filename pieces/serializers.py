from rest_framework import serializers
from .models import PieceJointe

class PieceJointeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PieceJointe
        fields = ['id', 'demande', 'nom', 'fichier', 'date_ajout']
