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
                pass
        if not user.is_verified:
            user.is_verified = True
            updated = True
        if not user.is_active:
            user.is_active = True
            updated = True
        if not user.role:
            user.role = 'fonctionnaire'
            updated = True
        if updated:
            user.save()