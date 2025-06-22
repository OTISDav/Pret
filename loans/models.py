# loans/models.py
from django.db import models
from django.conf import settings # Pour référencer le modèle User personnalisé
import uuid # Pour générer un numéro de demande unique et lisible

class LoanApplication(models.Model):
    # Statuts possibles pour une demande de prêt
    STATUS_CHOICES = (
        ('pending', 'En attente'),
        ('approved', 'Approuvé'),
        ('rejected', 'Rejeté'),
        ('disbursed', 'Décaissé'), # L'argent a été versé
        ('completed', 'Terminé'),  # Le prêt a été entièrement remboursé
        ('cancelled', 'Annulé'),   # Demande annulée par l'utilisateur ou l'admin
    )

    # Catégories de prêts
    LOAN_TYPE_CHOICES = (
        ('personal', 'Prêt Personnel'),
        ('housing', 'Prêt Immobilier'),
        ('vehicle', 'Prêt Véhicule'),
        ('education', 'Prêt Étudiant'),
        ('other', 'Autre'),
    )

    # Numéro de demande unique
    # Utilise UUID pour générer un identifiant plus complexe et non séquentiel
    # Le numéro sera tronqué pour être plus lisible
    application_number = models.CharField(
        max_length=50,
        unique=True,
        editable=False, # Ne peut pas être modifié manuellement
        default=uuid.uuid4, # Génère un UUID par défaut
        verbose_name="Numéro de Demande"
    )

    # Référence à l'utilisateur qui a fait la demande (Fonctionnaire)
    # Utilisez settings.AUTH_USER_MODEL pour référencer votre modèle User personnalisé
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='loan_applications',
        limit_choices_to={'role': 'fonctionnaire'}, # Seuls les fonctionnaires peuvent demander un prêt
        verbose_name="Demandeur"
    )

    # Informations sur le prêt demandé
    amount_requested = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Montant demandé"
    )
    loan_type = models.CharField(
        max_length=50,
        choices=LOAN_TYPE_CHOICES,
        default='personal',
        verbose_name="Type de prêt"
    )
    repayment_period_months = models.IntegerField(
        verbose_name="Durée de remboursement (mois)"
    )
    purpose = models.TextField(
        blank=True,
        verbose_name="Objectif du prêt"
    )

    # Statut de la demande
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Statut de la demande"
    )

    # Dates importantes
    date_submitted = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de soumission"
    )
    date_updated = models.DateTimeField(
        auto_now=True,
        verbose_name="Dernière mise à jour"
    )
    date_approved_rejected = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date d'approbation/rejet"
    )

    # Informations sur l'approbation/rejet
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, # Ne supprime pas l'application si l'admin est supprimé
        null=True,
        blank=True,
        related_name='approved_loan_applications',
        limit_choices_to={'role': 'administrateur'}, # Seuls les administrateurs peuvent approuver/rejeter
        verbose_name="Approuvé/Rejeté par"
    )
    admin_comments = models.TextField(
        blank=True,
        verbose_name="Commentaires de l'administrateur"
    )

    # Champ pour le montant approuvé (peut être différent du montant demandé)
    amount_approved = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Montant approuvé"
    )

    class Meta:
        verbose_name = "Demande de prêt"
        verbose_name_plural = "Demandes de prêt"
        ordering = ['-date_submitted'] # Tri par défaut : les plus récentes en premier

    def save(self, *args, **kwargs):
        # S'assurer que le numéro de demande est généré seulement lors de la première sauvegarde
        if not self.application_number:
            self.application_number = str(uuid.uuid4()).split('-')[0].upper() # Prend la première partie de l'UUID en majuscules

        # Si le statut passe à 'approved' ou 'rejected', enregistrer la date et le montant approuvé
        if self.status in ['approved', 'rejected', 'disbursed', 'completed', 'cancelled'] and not self.date_approved_rejected:
            self.date_approved_rejected = timezone.now()

        # Si le prêt est approuvé et qu'aucun montant approuvé n'est défini, utiliser le montant demandé
        if self.status == 'approved' and self.amount_approved is None:
            self.amount_approved = self.amount_requested

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Demande {self.application_number} par {self.applicant.username} - Statut: {self.status}"