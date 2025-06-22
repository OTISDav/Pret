from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from .models import LoanApplication
from .serializers import LoanApplicationSerializer, LoanApplicationAdminSerializer
from users.models import User


class IsFonctionnaire(permissions.BasePermission):
    """
    Permission personnalisée pour n'autoriser que les utilisateurs avec le rôle 'fonctionnaire'.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_active

    def has_object_permission(self, request, view, obj):
        return request.user.role == 'fonctionnaire' and obj.applicant == request.user

class IsAdministrateur(permissions.BasePermission):
    """
    Permission personnalisée pour n'autoriser que les utilisateurs avec le rôle 'administrateur'.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_active and request.user.role == 'administrateur'

    def has_object_permission(self, request, view, obj):
        return request.user.role == 'administrateur'


class LoanApplicationListCreateView(generics.ListCreateAPIView):
    """
    Vue pour lister les demandes de prêt d'un fonctionnaire et en créer une nouvelle.
    """
    serializer_class = LoanApplicationSerializer
    permission_classes = [permissions.IsAuthenticated, IsFonctionnaire]

    def get_queryset(self):
        if self.request.user.role == 'fonctionnaire':
            return LoanApplication.objects.filter(applicant=self.request.user).order_by('-date_submitted')
        return LoanApplication.objects.none()

    def perform_create(self, serializer):
        if not self.request.user.cin_number:
            raise serializers.ValidationError({"detail": "Votre numéro CIN doit être renseigné dans votre profil pour soumettre une demande de prêt."})
        if self.request.user.role != 'fonctionnaire':
            raise serializers.ValidationError({"detail": "Seuls les fonctionnaires peuvent soumettre des demandes de prêt."})
        serializer.save(applicant=self.request.user)

class LoanApplicationDetailView(generics.RetrieveUpdateAPIView):
    """
    Vue pour voir les détails d'une demande de prêt spécifique d'un fonctionnaire et la mettre à jour.
    Un fonctionnaire ne peut modifier que les demandes 'pending' ou 'rejected'.
    """
    queryset = LoanApplication.objects.all()
    serializer_class = LoanApplicationSerializer
    permission_classes = [permissions.IsAuthenticated, IsFonctionnaire]
    lookup_field = 'pk'

    def get_object(self):
        obj = get_object_or_404(self.get_queryset(), pk=self.kwargs['pk'])
        self.check_object_permissions(self.request, obj)
        return obj

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status not in ['pending', 'rejected']:
            return Response({"detail": f"Vous ne pouvez modifier une demande que si son statut est 'En attente' ou 'Rejeté'. Statut actuel : {instance.get_status_display()}."}, status=status.HTTP_400_BAD_REQUEST)
        mutable_data = request.data.copy()
        if 'status' in mutable_data:
            mutable_data.pop('status')
        if 'approved_by' in mutable_data:
            mutable_data.pop('approved_by')
        if 'admin_comments' in mutable_data:
            mutable_data.pop('admin_comments')
        if 'amount_approved' in mutable_data:
            mutable_data.pop('amount_approved')

        serializer = self.get_serializer(instance, data=mutable_data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

class LoanApplicationCancelView(APIView):
    """
    Vue pour permettre à un fonctionnaire d'annuler sa propre demande de prêt.
    """
    permission_classes = [permissions.IsAuthenticated, IsFonctionnaire]

    def post(self, request, pk):
        loan_application = get_object_or_404(LoanApplication, pk=pk, applicant=request.user)

        if loan_application.status not in ['pending', 'approved']:
            return Response({"detail": f"Impossible d'annuler une demande avec le statut '{loan_application.get_status_display()}'."}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            loan_application.status = 'cancelled'
            loan_application.admin_comments = f"Annulé par le demandeur le {loan_application.date_updated.strftime('%Y-%m-%d %H:%M')}"
            loan_application.save()

            context = {'loan': loan_application, 'user': request.user}

            subject_admin = f"Demande de prêt annulée : {loan_application.application_number}"
            html_message_admin = render_to_string('loans/email_loan_cancelled_admin.html', context)
            plain_message_admin = strip_tags(html_message_admin)
            admin_emails = User.objects.filter(role='administrateur', is_active=True).values_list('email', flat=True)
            if admin_emails:
                try:
                    send_mail(
                        subject_admin,
                        plain_message_admin,
                        settings.DEFAULT_FROM_EMAIL,
                        list(admin_emails),
                        html_message=html_message_admin,
                        fail_silently=False
                    )
                except Exception as e:
                    print(f"Erreur lors de l'envoi de l'e-mail d'annulation à l'admin: {e}")

            # Email au demandeur
            subject_applicant = f"Votre demande de prêt a été annulée : {loan_application.application_number}"
            html_message_applicant = render_to_string('loans/email_loan_cancelled_applicant.html', context)
            plain_message_applicant = strip_tags(html_message_applicant)
            try:
                send_mail(
                    subject_applicant,
                    plain_message_applicant,
                    settings.DEFAULT_FROM_EMAIL,
                    [loan_application.applicant.email],
                    html_message=html_message_applicant,
                    fail_silently=False
                )
            except Exception as e:
                print(f"Erreur lors de l'envoi de l'e-mail d'annulation au demandeur: {e}")


        return Response({"detail": "Demande de prêt annulée avec succès."}, status=status.HTTP_200_OK)


class AdminLoanApplicationListView(generics.ListAPIView):
    """
    Vue pour les administrateurs afin de lister toutes les demandes de prêt.
    Permet un filtrage et une recherche avancés.
    """
    queryset = LoanApplication.objects.all().select_related('applicant', 'approved_by').order_by('-date_submitted')
    serializer_class = LoanApplicationAdminSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdministrateur] # Seuls les admins peuvent accéder
    filterset_fields = ['status', 'loan_type', 'applicant__username', 'applicant__email']
    search_fields = ['application_number', 'applicant__username', 'applicant__email', 'purpose', 'admin_comments']

class AdminLoanApplicationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Vue pour les administrateurs afin de voir les détails, mettre à jour (approuver/rejeter)
    ou supprimer une demande de prêt.
    """
    queryset = LoanApplication.objects.all().select_related('applicant', 'approved_by')
    serializer_class = LoanApplicationAdminSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdministrateur]
    lookup_field = 'pk'

    def get_object(self):
        obj = get_object_or_404(self.get_queryset(), pk=self.kwargs['pk'])
        self.check_object_permissions(self.request, obj) # Vérifie IsAdministrateur
        return obj

    def perform_update(self, serializer):
        instance = serializer.save()

        context = {'loan': instance, 'admin_user': self.request.user}

        subject = f"Mise à jour de votre demande de prêt #{instance.application_number} - Statut : {instance.get_status_display()}"
        html_message = render_to_string('loans/email_loan_status_update.html', context)
        plain_message = strip_tags(html_message)

        try:
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [instance.applicant.email],
                html_message=html_message,
                fail_silently=False
            )
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'e-mail de mise à jour de statut à {instance.applicant.email}: {e}")

    def perform_destroy(self, instance):
        applicant_email = instance.applicant.email
        application_number = instance.application_number
        admin_user = self.request.user

        instance.delete()

        subject = f"Votre demande de prêt #{application_number} a été supprimée"
        message = f"""
        Cher {applicant_email.split('@')[0]},

        Nous vous informons que votre demande de prêt numéro {application_number} a été supprimée par l'administrateur {admin_user.username}.

        Cordialement,
        L'équipe de la plateforme de prêt
        """
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [applicant_email],
                fail_silently=False
            )
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'e-mail de suppression à {applicant_email}: {e}")