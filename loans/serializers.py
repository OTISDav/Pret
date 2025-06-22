from rest_framework import serializers
from .models import LoanApplication
from users.serializers import UserProfileSerializer

class LoanApplicationSerializer(serializers.ModelSerializer):
    applicant = UserProfileSerializer(read_only=True)
    cin_number = serializers.CharField(write_only=True, required=False)
    class Meta:
        model = LoanApplication
        fields = [
            'id', 'application_number', 'applicant', 'cin_number', 'amount_requested',
            'loan_type', 'repayment_period_months', 'purpose', 'status',
            'date_submitted', 'date_updated', 'date_approved_rejected',
            'approved_by', 'admin_comments', 'amount_approved'
        ]
        read_only_fields = [
            'application_number', 'status', 'date_submitted', 'date_updated',
            'date_approved_rejected', 'approved_by', 'admin_comments', 'amount_approved'
        ]

    def create(self, validated_data):
        validated_data.pop('cin_number', None)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data.pop('cin_number', None)

        return super().update(instance, validated_data)


class LoanApplicationAdminSerializer(serializers.ModelSerializer):
    applicant = UserProfileSerializer(read_only=True)
    approved_by = UserProfileSerializer(read_only=True)

    class Meta:
        model = LoanApplication
        fields = [
            'id', 'application_number', 'applicant', 'amount_requested',
            'loan_type', 'repayment_period_months', 'purpose', 'status',
            'date_submitted', 'date_updated', 'date_approved_rejected',
            'approved_by', 'admin_comments', 'amount_approved'
        ]
        read_only_fields = ['application_number', 'date_submitted', 'date_updated']
    def validate(self, data):
        if 'status' in data:
            new_status = data['status']
            current_status = self.instance.status if self.instance else 'pending'

            if new_status in ['approved', 'rejected'] and not data.get('admin_comments'):
                raise serializers.ValidationError({
                    "admin_comments": "Un commentaire est requis lors de l'approbation ou du rejet."
                })

            if self.instance:
                if current_status in ['approved', 'rejected', 'disbursed', 'completed', 'cancelled'] and new_status == 'pending':
                    raise serializers.ValidationError({
                        "status": f"Impossible de passer de '{current_status}' à 'pending'."
                    })
                if current_status in ['completed', 'cancelled'] and new_status != current_status:
                     raise serializers.ValidationError({
                        "status": f"Impossible de modifier le statut d'une demande '{current_status}'."
                    })
                status_order = {
                    'pending': 0, 'approved': 1, 'disbursed': 2, 'completed': 3,
                    'rejected': 98, 'cancelled': 99
                }
                if status_order.get(new_status, -1) < status_order.get(current_status, -1) and new_status not in ['rejected', 'cancelled']:
                    if not (new_status in ['rejected', 'cancelled'] and current_status not in ['completed', 'cancelled']):
                        raise serializers.ValidationError({
                            "status": f"Transition de statut invalide de '{current_status}' à '{new_status}'."
                        })
        return data

    def update(self, instance, validated_data):
        new_status = validated_data.get('status', instance.status)

        if new_status != instance.status:
            request_user = self.context.get('request').user
            if request_user and request_user.role == 'administrateur':
                if new_status in ['approved', 'rejected']:
                    instance.approved_by = request_user
                    instance.date_approved_rejected = timezone.now()
                elif instance.status in ['approved', 'rejected'] and new_status not in ['approved', 'rejected']:
                    instance.approved_by = None
                    instance.date_approved_rejected = None
            else:
                raise serializers.ValidationError({"detail": "Seuls les administrateurs peuvent modifier le statut ou les commentaires."})

        if new_status == 'approved' and validated_data.get('amount_approved') is None and instance.amount_approved is None:
            instance.amount_approved = instance.amount_requested

        return super().update(instance, validated_data)