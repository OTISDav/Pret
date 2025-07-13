from rest_framework import generics, permissions
from .models import PieceJointe
from .serializers import PieceJointeSerializer

class PieceJointeUploadView(generics.CreateAPIView):
    serializer_class = PieceJointeSerializer
    permission_classes = [permissions.IsAuthenticated]
