# users/views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
import jwt
from django.utils import timezone
import datetime

from .models import User
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    PasswordChangeSerializer,
    AdminUserManagementSerializer
)

# --- Vues d'Authentification ---

class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        # L'utilisateur est créé comme INACTIF et NON VÉRIFIÉ par défaut.
        # L'activation par email mettra is_active et is_verified à True.
        user = serializer.save(is_active=False, is_verified=False)

        # Générer un token d'activation JWT
        payload = {
            'user_id': user.id,
            'exp': (timezone.now() + datetime.timedelta(hours=24)).timestamp(), # Expire dans 24 heures
            'type': 'email_verification'
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

        # Construire l'URL d'activation pour le frontend React
        activation_link = f"{settings.FRONTEND_URL}/activate?token={token}"

        # Envoyer l'e-mail d'activation
        subject = 'Activez votre compte pour la plateforme de prêt'
        message = f"""
        Cher {user.first_name if user.first_name else user.username},

        Merci de vous être inscrit sur notre plateforme de prêt.
        Pour activer votre compte, veuillez cliquer sur le lien ci-dessous :

        {activation_link}

        Ce lien expirera dans 24 heures.

        Si vous n'avez pas créé de compte, veuillez ignorer cet e-mail.

        Cordialement,
        L'équipe de la plateforme de prêt
        """
        email_from = settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@votreapp.com'
        recipient_list = [user.email]

        try:
            send_mail(subject, message, email_from, recipient_list, fail_silently=False)
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'e-mail d'activation à {user.email}: {e}")
            # En production, vous pourriez envisager de marquer l'utilisateur d'une certaine façon
            # ou d'avoir un système de nouvelle tentative d'envoi d'e-mail.
            # Pour l'instant, on renvoie une erreur au client si l'envoi échoue.
            return Response({"detail": "Votre compte a été créé, mais nous n'avons pas pu envoyer l'e-mail d'activation. Veuillez contacter l'administrateur.", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"detail": "Un lien d'activation a été envoyé à votre adresse e-mail. Veuillez vérifier votre boîte de réception pour activer votre compte."}, status=status.HTTP_201_CREATED)

class UserLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username_or_email = serializer.validated_data.get('username_or_email')
        password = serializer.validated_data.get('password')

        # Tenter d'authentifier par username ou email
        user = authenticate(request, username=username_or_email, password=password)
        if not user:
            try:
                user = User.objects.get(email=username_or_email)
                if not user.check_password(password):
                    user = None
            except User.DoesNotExist:
                user = None

        if user is not None:
            # Vérifier si le compte est vérifié par email.
            # Les comptes staff/superuser sont exemptés de cette vérification par e-mail
            # car ils sont généralement créés par l'administrateur directement.
            if not user.is_verified and not user.is_staff and not user.is_superuser:
                return Response({"detail": "Votre compte n'a pas encore été vérifié par e-mail. Veuillez vérifier votre boîte de réception pour le lien d'activation."}, status=status.HTTP_403_FORBIDDEN)

            # Vérifier si le compte est actif (peut être désactivé manuellement par un administrateur)
            if not user.is_active:
                return Response({"detail": "Votre compte est désactivé par l'administrateur. Veuillez le contacter."}, status=status.HTTP_403_FORBIDDEN)

            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserProfileSerializer(user).data
            }, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Identifiants invalides."}, status=status.HTTP_401_UNAUTHORIZED)

class UserLogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Déconnexion réussie."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"detail": "Token invalide ou manquant.", "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class AccountActivationView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        token = request.query_params.get('token')

        if not token:
            return Response({"detail": "Token d'activation manquant."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])

            if payload.get('type') != 'email_verification':
                return Response({"detail": "Token invalide."}, status=status.HTTP_400_BAD_REQUEST)

            if payload.get('exp') < timezone.now().timestamp():
                return Response({"detail": "Le lien d'activation a expiré. Veuillez demander un nouveau lien."}, status=status.HTTP_400_BAD_REQUEST)

            user_id = payload.get('user_id')
            user = User.objects.get(id=user_id)

            if user.is_verified and user.is_active:
                return Response({"detail": "Votre compte est déjà activé et vérifié."}, status=status.HTTP_200_OK)

            # Si le compte n'est ni vérifié ni actif, on l'active via ce lien
            user.is_verified = True
            user.is_active = True
            user.save()

            return Response({"detail": "Votre compte a été activé avec succès. Vous pouvez maintenant vous connecter."}, status=status.HTTP_200_OK)

        except jwt.ExpiredSignatureError:
            return Response({"detail": "Le lien d'activation a expiré. Veuillez demander un nouveau lien."}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.InvalidTokenError:
            return Response({"detail": "Token d'activation invalide."}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"detail": "Utilisateur introuvable pour ce token."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"Erreur inattendue lors de l'activation du compte: {e}")
            return Response({"detail": "Une erreur est survenue lors de l'activation de votre compte."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ... (Le reste des vues UserProfileView, PasswordChangeView, AdminUserListView, AdminUserDetailView restent inchangées)
# --- Vues de Profil Utilisateur ---

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

class PasswordChangeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        old_password = serializer.validated_data.get('old_password')
        new_password = serializer.validated_data.get('new_password')

        if not user.check_password(old_password):
            return Response({"old_password": "L'ancien mot de passe est incorrect."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        # Invalider les sessions JWT actives de l'utilisateur (optionnel, mais bonne pratique)
        # Ceci force une nouvelle connexion avec le nouveau mot de passe
        try:
            refresh_token = request.data.get("refresh_token")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
        except Exception:
            pass # Gérer si le refresh token n'est pas fourni ou est invalide

        return Response({"detail": "Mot de passe modifié avec succès. Veuillez vous reconnecter."}, status=status.HTTP_200_OK)

# --- Vues de Gestion Admin des Utilisateurs ---

class AdminUserListView(generics.ListAPIView):
    queryset = User.objects.all().order_by('email')
    serializer_class = AdminUserManagementSerializer
    permission_classes = [permissions.IsAdminUser]

class AdminUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = AdminUserManagementSerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'pk'

    def get_object(self):
        return get_object_or_404(User, pk=self.kwargs.get('pk'))

    def perform_update(self, serializer):
        # Empêcher un admin de rétrograder son propre compte superuser ou staff
        if self.request.user == serializer.instance:
            if not serializer.validated_data.get('is_superuser', serializer.instance.is_superuser) and serializer.instance.is_superuser:
                raise serializers.ValidationError({"detail": "Vous ne pouvez pas rétrograder votre propre compte super-utilisateur."})
            if not serializer.validated_data.get('is_staff', serializer.instance.is_staff) and serializer.instance.is_staff and not serializer.instance.is_superuser:
                 raise serializers.ValidationError({"detail": "Vous ne pouvez pas rétrograder votre propre compte staff si vous n'êtes pas super-utilisateur."})

        serializer.save()