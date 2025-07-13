from rest_framework import serializers
from .models import Message

class MessageSerializer(serializers.ModelSerializer):
    auteur_email = serializers.ReadOnlyField(source='auteur.email')

    class Meta:
        model = Message
        fields = ['id', 'demande', 'auteur_email', 'contenu', 'date_envoi', 'lu']
        read_only_fields = ['auteur_email', 'date_envoi', 'lu']
