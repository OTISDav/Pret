from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def send_loan_status_email(loan_application):
    """
    Envoie un e-mail à l'applicant pour l'informer du changement de statut de sa demande de prêt.
    """
    subject = f"Mise à jour de votre demande de prêt #{loan_application.application_number}"
    recipient_email = loan_application.applicant.email
    context = {
        'loan': loan_application,
        'applicant_username': loan_application.applicant.username,
        'status_display': loan_application.get_status_display(),
        'admin_comments': loan_application.admin_comments,
        'amount_approved': loan_application.amount_approved,
    }
    html_message = render_to_string('emails/loan_status_update.html', context)
    plain_message = strip_tags(html_message)  # Version texte brut pour les clients mail qui ne supportent pas HTML

    try:
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient_email],
            html_message=html_message,
            fail_silently=False,
        )
        print(f"Email de statut envoyé à {recipient_email} pour le prêt #{loan_application.application_number}")
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email de statut à {recipient_email}: {e}")