from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')), # Inclut les URLs de l'app users
    path('api/loans/', include('loans.urls')),
    path('api/pieces/', include('pieces.urls')),
    path('api/messagerie/', include('messagerie.urls')),


    path('auth/', include('drf_social_oauth2.urls', namespace='drf')),

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),  #
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)