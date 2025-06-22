# users/pipeline.py
from users.models import User
from django.db import transaction


@transaction.atomic
def save_profile(backend, user, response, *args, **kwargs):
    updated = False

    if backend.name == 'google-oauth2':
        first_name = response.get('given_name')
        last_name = response.get('family_name')
        email = response.get('email')

        if first_name and user.first_name != first_name:
            user.first_name = first_name
            updated = True
        if last_name and user.last_name != last_name:
            user.last_name = last_name
            updated = True

        if email and user.email != email:
            if not User.objects.filter(email=email).exclude(pk=user.pk).exists():
                user.email = email
                updated = True
            else:
                # Si l'email social est déjà prise par un autre compte local,
                # ne pas mettre à jour l'email pour éviter un conflit.
                # L'utilisateur se connectera avec l'email liée au compte Google.
                pass

        # Pour les comptes Google, l'email est considérée comme vérifiée
        if not user.is_verified:
            user.is_verified = True
            updated = True

        # Les comptes créés via Google sont actifs par défaut
        if not user.is_active:
            user.is_active = True
            updated = True

        # S'assurer que le rôle est "fonctionnaire" par défaut si c'est une nouvelle inscription via Google
        if not user.role:  # Si le rôle n'est pas encore défini (première connexion sociale)
            user.role = 'fonctionnaire'
            updated = True

        if updated:
            user.save()