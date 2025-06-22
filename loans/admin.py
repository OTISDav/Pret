# loans/admin.py
from django.contrib import admin
from .models import LoanApplication

@admin.register(LoanApplication)
class LoanApplicationAdmin(admin.ModelAdmin):
    list_display = ('application_number', 'applicant', 'amount_requested', 'status', 'date_submitted', 'approved_by', 'amount_approved')
    list_filter = ('status', 'loan_type', 'date_submitted', 'date_approved_rejected')
    search_fields = ('application_number', 'applicant__username', 'applicant__email', 'purpose', 'admin_comments')
    raw_id_fields = ('applicant', 'approved_by')
    readonly_fields = ('application_number', 'date_submitted', 'date_updated', 'date_approved_rejected')
    fieldsets = (
        (None, {'fields': ('applicant', 'application_number', 'status')}),
        ('Détails de la demande', {'fields': ('amount_requested', 'loan_type', 'repayment_period_months', 'purpose')}),
        ('Décision Administrative', {'fields': ('approved_by', 'amount_approved', 'admin_comments', 'date_approved_rejected')}),
        ('Horodatages', {'fields': ('date_submitted', 'date_updated')}),
    )