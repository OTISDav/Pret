from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('fonctionnaire', 'Fonctionnaire'),
        ('administrateur', 'Administrateur'),
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='fonctionnaire',
        verbose_name="Rôle de l'utilisateur"
    )

    phone_number = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True,
        verbose_name="Numéro de téléphone"
    )
    cin_number = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True,
        verbose_name="Numéro d'Identification National (CIN)"
    )

    email = models.EmailField(unique=True, verbose_name="Adresse e-mail")

    is_verified = models.BooleanField(default=False, verbose_name="Email vérifié")


    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"

    def __str__(self):
        return self.email