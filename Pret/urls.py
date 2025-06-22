from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')), # Inclut les URLs de l'app users
    path('api/loans/', include('loans.urls')),

    # URLs pour social auth et OAuth2 (Google Login)
    path('auth/', include('drf_social_oauth2.urls', namespace='drf')),

    # --- URLs pour la documentation Swagger/OpenAPI ---
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),  # Point de terminaison du schéma OpenAPI
    # Optional UI:
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    # Interface Swagger UI
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),  # Interface Redoc
    # --- Fin des URLs pour la documentation ---

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)