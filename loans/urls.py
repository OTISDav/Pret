# loans/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # URLs pour les Fonctionnaires (utilisateur connecté)
    path('', views.LoanApplicationListCreateView.as_view(), name='loan_application_list_create'),
    path('<int:pk>/', views.LoanApplicationDetailView.as_view(), name='loan_application_detail'),
    path('<int:pk>/cancel/', views.LoanApplicationCancelView.as_view(), name='loan_application_cancel'),



    # URLs pour les Administrateurs
    path('admin/', views.AdminLoanApplicationListView.as_view(), name='admin_loan_application_list'),
    path('admin/<int:pk>/', views.AdminLoanApplicationDetailView.as_view(), name='admin_loan_application_detail'),
]