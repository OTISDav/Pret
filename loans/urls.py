from django.urls import path
from .views import (
    DemandePretCreateView, MesDemandesView, DemandePretDetailView,
    ChangerStatutView
)

urlpatterns = [
    path('soumettre/', DemandePretCreateView.as_view(), name='soumettre-pret'),
    path('mes-demandes/', MesDemandesView.as_view(), name='mes-demandes'),
    path('detail/<int:pk>/', DemandePretDetailView.as_view(), name='detail-pret'),
    path('changer-statut/<int:pk>/', ChangerStatutView.as_view(), name='changer-statut'),
]
