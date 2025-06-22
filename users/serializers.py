# users/serializers.py
from rest_framework import serializers
from .models import User

# --- Serializers pour l'Authentification ---

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2', 'first_name', 'last_name', 'phone_number', 'cin_number', 'role')
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False},
            'phone_number': {'required': False},
            'cin_number': {'required': False},
            'role': {'required': False}
        }

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Les deux mots de passe ne correspondent pas."})
        if 'role' in data and data['role'] != 'fonctionnaire':
            data['role'] = 'fonctionnaire' # Force le rôle à fonctionnaire à l'inscription normale
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        # À l'inscription normale, le compte n'est pas actif ni vérifié par défaut
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone_number=validated_data.get('phone_number'),
            cin_number=validated_data.get('cin_number'),
            role=validated_data.get('role', 'fonctionnaire'),
            is_active=False, # Inactif jusqu'à vérification email
            is_verified=False # Non vérifié jusqu'à activation
        )
        return user

class UserLoginSerializer(serializers.Serializer):
    username_or_email = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    def validate(self, data):
        username_or_email = data.get('username_or_email')
        password = data.get('password')

        if not username_or_email or not password:
            raise serializers.ValidationError("Le nom d'utilisateur/email et le mot de passe sont requis.")

        return data

# --- Serializers pour le Profil Utilisateur ---

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'phone_number', 'cin_number', 'role', 'is_verified', 'date_joined', 'last_login')
        read_only_fields = ('id', 'username', 'email', 'role', 'is_verified', 'date_joined', 'last_login')

class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, style={'input_type': 'password'})
    new_password = serializers.CharField(required=True, style={'input_type': 'password'})
    confirm_new_password = serializers.CharField(required=True, style={'input_type': 'password'})

    def validate(self, data):
        if data['new_password'] != data['confirm_new_password']:
            raise serializers.ValidationError({"new_password": "Les nouveaux mots de passe ne correspondent pas."})
        return data

# --- Serializers pour la Gestion Admin des Utilisateurs ---

class AdminUserManagementSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'phone_number', 'cin_number', 'role', 'is_active', 'is_staff', 'is_verified', 'date_joined', 'last_login')
        read_only_fields = ('date_joined', 'last_login')

    def update(self, instance, validated_data):
        instance.role = validated_data.get('role', instance.role)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.is_staff = validated_data.get('is_staff', instance.is_staff)
        instance.is_verified = validated_data.get('is_verified', instance.is_verified)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.cin_number = validated_data.get('cin_number', instance.cin_number)
        instance.save()
        return instance