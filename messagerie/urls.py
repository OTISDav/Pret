from django.urls import path
from .views import MessageListCreateView, MesMessagesView

urlpatterns = [
    path('demandes/<int:demande_id>/messages/', MessageListCreateView.as_view(), name='demande-messages'),
    path('mes-messages/', MesMessagesView.as_view(), name='mes-messages'),

]
