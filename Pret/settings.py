import os
from pathlib import Path
from datetime import timedelta
BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = 'votre_cle_secrete_django_ici' # TRÈS IMPORTANT : Changez ceci pour une clé complexe et unique

DEBUG = True # Mettez à False en production

ALLOWED_HOSTS = [] # Ajoutez les noms de domaine de votre serveur en production, ex: ['www.votredomaine.com', '127.0.0.1']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'drf_spectacular',
    'django_filters',
    'corsheaders',

    # Mes applications
    'users',
    'loans', # Nous allons la développer après

    'pieces',
    'messagerie',

    # Django REST Framework
    'rest_framework',
    'rest_framework_simplejwt', # Pour JWT

    # Django OAuth2 Toolkit & Social Auth
    'oauth2_provider',
    'social_django',
    'drf_social_oauth2',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware', # Important pour gérer les erreurs de Social Auth
]


CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000", # ou le port de votre frontend React (ex: 5173 pour Vite par défaut)
    "http://127.0.0.1:3000", # ou le port de votre frontend React
    "http://localhost:5173", # Ajoutez celui-ci si Vite utilise le port 5173
    "http://127.0.0.1:5173", # Ajoutez celui-ci si Vite utilise le port 5173
]

CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization", # TRÈS IMPORTANT pour les tokens JWT
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

CORS_ALLOW_CREDENTIALS = True # Si vous avez besoin d'envoyer des cookies ou des en-têtes d'autorisation complexes

ROOT_URLCONF = 'Pret.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends', # Pour Social Auth
                'social_django.context_processors.login_redirect', # Pour Social Auth
            ],
        },
    },
]

WSGI_APPLICATION = 'Pret.wsgi.application'



DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}



# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'fr-tg' # Langue et localisation pour le Togo
TIME_ZONE = 'Africa/Lome' # Fuseau horaire pour Lomé, Togo
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles') # Où les fichiers statiques seront collectés pour le déploiement

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media') # Où les fichiers téléchargés par les utilisateurs seront stockés

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# --- Custom User Model ---
AUTH_USER_MODEL = 'users.User' # Indique à Django d'utiliser notre modèle User personnalisé


# --- Django REST Framework Settings ---
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'oauth2_provider.contrib.rest_framework.OAuth2Authentication', # Pour OAuth2 (social login)
        'rest_framework_simplejwt.authentication.JWTAuthentication', # Pour JWT (login classique)
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated', # Par défaut, toutes les vues nécessitent une authentification
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema', # <--- Assurez-vous que cette ligne est ici
    'DEFAULT_FILTER_BACKENDS': ( # <--- Assurez-vous que ce bloc est ici
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
}




# --- Simple JWT Settings ---
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60), # Durée de vie du token d'accès
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),    # Augmenté pour la commodité, à ajuster
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}


# --- Django OAuth2 Toolkit Settings ---
OAUTH2_PROVIDER = {
    'ACCESS_TOKEN_EXPIRE_SECONDS': 3600, # 1 heure
    'REFRESH_TOKEN_EXPIRE_SECONDS': 86400 * 7, # 7 jours
    'SCOPES': {
        'read': 'Read scope',
        'write': 'Write scope',
        'groups': 'Access to your groups',
        'email': 'Access to your email',
        'profile': 'Access to your profile',
    },
    'PKCE_REQUIRED': False, # Peut être True en production pour plus de sécurité avec "Authorization code" flow
}

# --- Python Social Auth Settings ---
AUTHENTICATION_BACKENDS = (
    # Google OAuth2
    'social_core.backends.google.GoogleOAuth2',
    # Django-rest-framework-social-oauth2 (utilise un backend OAuth2 générique pour les tokens)
    'drf_social_oauth2.backends.DjangoOAuth2',
    # Django ModelBackend (pour l'authentification classique par nom d'utilisateur/mot de passe)
    'django.contrib.auth.backends.ModelBackend',
)

# Clés d'API Google (TRÈS IMPORTANT !)
# REMPLACEZ CES VALEURS PAR VOS PROPRES CLES GOOGLE CLOUD CONSOLE
# instructions pour les obtenir: https://console.developers.google.com/
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ.get('GOOGLE_OAUTH2_KEY', '615623893148-62ohdnlm73tnqdrdil0kdf1guti02r9t.apps.googleusercontent.com')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ.get('GOOGLE_OAUTH2_SECRET', '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')

# URL de redirection après connexion réussie via social auth
SOCIAL_AUTH_URL_NAMESPACE = 'social'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Mappage des champs du profil social vers votre modèle User personnalisé
SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.user.create_user',
    'users.pipeline.save_profile', # Notre pipeline personnalisé
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
)


# --- Configuration Email ---
# Pour le développement, voir les emails dans la console

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587             # Port standard pour le chiffrement TLS (STARTTLS)
EMAIL_USE_TLS = True         # Active le chiffrement TLS
# EMAIL_USE_SSL = False      # Ne pas activer SSL si TLS est activé (mutuellement exclusifs)

EMAIL_HOST_USER = 'ddavidotis@gmail.com'  # Votre adresse Gmail complète
EMAIL_HOST_PASSWORD = 'exdx huxd gkli bbdb' # Le mot de passe de 16 caractères généré
DEFAULT_FROM_EMAIL = 'Pret <ddavidotis@gmail.com>' # L'adresse d'envoi visible pour les destinataires
SERVER_EMAIL = DEFAULT_FROM_EMAIL # Email pour les messages d'erreur du serveur Django

# N'oubliez pas le SECRET_KEY dans votre settings.py, il est essentiel pour JWT et les tokens d'activation
# SECRET_KEY = '...'

# Pour l'envoi d'emails réels (décommenter et configurer pour la production)
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
# EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
# EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true'
# EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'votre_email@gmail.com')
# EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'votre_mot_de_passe_app_gmail')
# DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'no-reply@votreapp.com')
# SERVER_EMAIL = DEFAULT_FROM_EMAIL


# --- URL de base de votre frontend React ---
# Utilisé pour les liens d'activation d'email et les redirections post-connexion Google
FRONTEND_URL = 'http://localhost:8000/api/users' # Changez ceci pour l'URL de votre frontend React en production !

# CORS_ORIGIN_WHITELIST = ['http://localhost:3000', 'http://127.0.0.1:3000'] # Si vous utilisez django-cors-headers
# CORS_ALLOW_CREDENTIALS = True # Si vous utilisez des cookies ou headers d'autorisation

# loan_platform/settings.py

