from django.urls import path
from .views import PieceJointeUploadView

urlpatterns = [
    path('upload/', PieceJointeUploadView.as_view(), name='upload-piece-jointe'),
]
