from rest_framework import generics, permissions
from .models import Message
from .serializers import MessageSerializer
from loans.models import DemandePret
from rest_framework.exceptions import PermissionDenied

class MessageListCreateView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        demande_id = self.kwargs['demande_id']
        user = self.request.user
        if user.is_staff:
            return Message.objects.filter(demande_id=demande_id)
        else:
            return Message.objects.filter(demande_id=demande_id, demande__fonctionnaire=user)

    def perform_create(self, serializer):
        demande_id = self.kwargs['demande_id']
        demande = DemandePret.objects.get(id=demande_id)
        user = self.request.user
        if not user.is_staff and demande.fonctionnaire != user:
            raise PermissionDenied("Vous ne pouvez pas envoyer un message sur une demande qui ne vous appartient pas.")
        serializer.save(auteur=user, demande=demande)


class MesMessagesView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Message.objects.all()
        return Message.objects.filter(auteur=user)

