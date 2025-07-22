from django.urls import reverse
from django.utils.html import format_html
from django.contrib import admin
from .models import Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['demande', 'auteur', 'auteur_last_name', 'contenu', 'date_envoi', 'lu']
    readonly_fields = ['date_envoi', 'lu']

    def save_model(self, request, obj, form, change):
        if not obj.pk:  # Si c'est un nouvel objet
            obj.auteur = request.user
        super().save_model(request, obj, form, change)

    def auteur_last_name(self, obj):
        return obj.auteur.last_name

    auteur_last_name.short_description = "Nom de l'auteur"

    def repondre_link(self, obj):
        # Remplace 'messagerie' par le nom réel de ton app
        url = reverse("admin:messagerie_message_add") + f"?demande={obj.demande.id}"
        return format_html(f'<a class="button" href="{url}">Répondre</a>')
    repondre_link.short_description = "Répondre"

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        demande_id = request.GET.get("demande")
        if demande_id:
            initial["demande"] = demande_id
        return initial
