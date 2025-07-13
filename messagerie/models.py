from django.db import models
from django.conf import settings
from loans.models import DemandePret

class Message(models.Model):
    demande = models.ForeignKey(DemandePret, on_delete=models.CASCADE, related_name='messages')
    auteur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    contenu = models.TextField()
    date_envoi = models.DateTimeField(auto_now_add=True)
    lu = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.auteur.email} → {self.demande.numero_dossier} [{self.date_envoi}]"
