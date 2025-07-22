from rest_framework import generics, permissions

from .models import DemandePret, HistoriqueStatut
from .serializers import (
    DemandePretSerializer, DemandePretCreateSerializer,
    HistoriqueStatutSerializer
)

# ✅ Soumission de demande (fonctionnaire)
class DemandePretCreateView(generics.CreateAPIView):
    serializer_class = DemandePretCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(fonctionnaire=self.request.user)

# ✅ Liste des demandes de l'utilisateur connecté
class MesDemandesView(generics.ListAPIView):
    serializer_class = DemandePretSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:  # ou user.role == 'administrateur'
            return DemandePret.objects.all()
        return DemandePret.objects.filter(fonctionnaire=user)

# ✅ Détail d’une demande
class DemandePretDetailView(generics.RetrieveAPIView):
    queryset = DemandePret.objects.all()
    serializer_class = DemandePretSerializer
    permission_classes = [permissions.IsAuthenticated]

# ✅ Mise à jour du statut (admin)
class ChangerStatutView(generics.UpdateAPIView):
    queryset = DemandePret.objects.all()
    serializer_class = HistoriqueStatutSerializer
    permission_classes = [permissions.IsAdminUser]

    def perform_update(self, serializer):
        demande = self.get_object()
        nouveau_statut = serializer.validated_data['statut']
        commentaire = serializer.validated_data.get('commentaire', '')

        # créer l'historique
        HistoriqueStatut.objects.create(
            demande=demande,
            statut=nouveau_statut,
            commentaire=commentaire
        )

        # mettre à jour la demande
        demande.statut = nouveau_statut
        demande.save()
