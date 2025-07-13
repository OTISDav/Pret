from django.db import models
from loans.models import DemandePret

class PieceJointe(models.Model):
    demande = models.ForeignKey(DemandePret, on_delete=models.CASCADE, related_name='pieces_jointes')
    nom = models.CharField(max_length=255)
    fichier = models.FileField(upload_to='pieces_jointes/')
    date_ajout = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nom} pour {self.demande.numero_dossier}"
