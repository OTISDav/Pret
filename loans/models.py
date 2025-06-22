from django.db import models
from django.conf import settings
import uuid

class LoanApplication(models.Model):
    STATUS_CHOICES = (
        ('pending', 'En attente'),
        ('approved', 'Approuvé'),
        ('rejected', 'Rejeté'),
        ('disbursed', 'Décaissé'),
        ('completed', 'Terminé'),
        ('cancelled', 'Annulé'),
    )
    LOAN_TYPE_CHOICES = (
        ('personal', 'Prêt Personnel'),
        ('housing', 'Prêt Immobilier'),
        ('vehicle', 'Prêt Véhicule'),
        ('education', 'Prêt Étudiant'),
        ('other', 'Autre'),
    )
    application_number = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        default=uuid.uuid4,
        verbose_name="Numéro de Demande"
    )
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='loan_applications',
        limit_choices_to={'role': 'fonctionnaire'},
        verbose_name="Demandeur"
    )
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
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Statut de la demande"
    )
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
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_loan_applications',
        limit_choices_to={'role': 'administrateur'},
        verbose_name="Approuvé/Rejeté par"
    )
    admin_comments = models.TextField(
        blank=True,
        verbose_name="Commentaires de l'administrateur"
    )
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
        ordering = ['-date_submitted']

    def save(self, *args, **kwargs):
        if not self.application_number:
            self.application_number = str(uuid.uuid4()).split('-')[0].upper()
        if self.status in ['approved', 'rejected', 'disbursed', 'completed', 'cancelled'] and not self.date_approved_rejected:
            self.date_approved_rejected = timezone.now()
        if self.status == 'approved' and self.amount_approved is None:
            self.amount_approved = self.amount_requested

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Demande {self.application_number} par {self.applicant.username} - Statut: {self.status}"