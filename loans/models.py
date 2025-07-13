import datetime
from django.utils.crypto import get_random_string
from django.db import models
from users.models import User



class TypePret(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.nom


class DemandePret(models.Model):
    STATUT_CHOICES = [
        ('soumis', 'Soumis'),
        ('en_cours', 'En cours de traitement'),
        ('accepte', 'Accepté'),
        ('refuse', 'Refusé'),
        ('archive', 'Archivé'),
    ]

    fonctionnaire = models.ForeignKey(User, on_delete=models.CASCADE, related_name="demandes")
    type_pret = models.ForeignKey(TypePret, on_delete=models.SET_NULL, null=True)
    montant = models.DecimalField(max_digits=12, decimal_places=2)
    duree_remboursement = models.IntegerField(help_text="Durée en mois")
    adresse_bien = models.TextField()
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='soumis')
    numero_dossier = models.CharField(max_length=100, unique=True)
    date_soumission = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.numero_dossier:
            today = datetime.date.today().strftime('%Y%m%d')
            random_id = get_random_string(5).upper()
            self.numero_dossier = f"PRT-{today}-{random_id}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.numero_dossier} - {self.fonctionnaire.email}"



class HistoriqueStatut(models.Model):
    demande = models.ForeignKey(DemandePret, on_delete=models.CASCADE, related_name='historiques')
    statut = models.CharField(max_length=20, choices=DemandePret.STATUT_CHOICES)
    date_modification = models.DateTimeField(auto_now_add=True)
    commentaire = models.TextField(blank=True)

    def __str__(self):
        return f"{self.demande.numero_dossier} - {self.statut}"
