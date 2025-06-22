# loans/serializers.py
from rest_framework import serializers
from .models import LoanApplication
from users.serializers import UserProfileSerializer # Pour inclure les infos du demandeur

class LoanApplicationSerializer(serializers.ModelSerializer):
    # Utilisez un sérialiseur imbriqué pour afficher les détails du demandeur
    # plutot que juste son ID. `read_only=True` car l'applicant est défini automatiquement
    # lors de la création d'une demande par l'utilisateur connecté.
    applicant = UserProfileSerializer(read_only=True)

    # Champ pour le CIN de l'utilisateur lors de la création/mise à jour
    # `write_only=True` pour qu'il ne soit pas inclus dans les réponses GET
    # `source='applicant.cin_number'` indique que ce champ vient du modèle User lié
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
        # L'applicant est défini dans la vue à partir de request.user
        # donc on le retire du validated_data ici.
        validated_data.pop('cin_number', None) # Le CIN est géré dans la vue ou par le UserProfileSerializer

        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Le CIN n'est pas censé être mis à jour via ce sérialiseur de prêt
        validated_data.pop('cin_number', None)

        return super().update(instance, validated_data)


class LoanApplicationAdminSerializer(serializers.ModelSerializer):
    # Pour l'admin, nous voulons un contrôle total et afficher plus de détails sur l'applicant
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
        read_only_fields = ['application_number', 'date_submitted', 'date_updated'] # L'admin peut modifier d'autres champs

    def validate(self, data):
        # Valider que si le statut est approuvé ou rejeté, un commentaire admin est fourni
        if 'status' in data:
            new_status = data['status']
            current_status = self.instance.status if self.instance else 'pending' # Pour les mises à jour

            if new_status in ['approved', 'rejected'] and not data.get('admin_comments'):
                raise serializers.ValidationError({
                    "admin_comments": "Un commentaire est requis lors de l'approbation ou du rejet."
                })

            # Empêcher les changements de statut non logiques
            if self.instance: # Si c'est une mise à jour d'instance existante
                # Une fois approuvé/rejeté, le statut ne devrait pas revenir à 'pending'
                if current_status in ['approved', 'rejected', 'disbursed', 'completed', 'cancelled'] and new_status == 'pending':
                    raise serializers.ValidationError({
                        "status": f"Impossible de passer de '{current_status}' à 'pending'."
                    })
                # Les prêts terminés/annulés ne peuvent plus être modifiés
                if current_status in ['completed', 'cancelled'] and new_status != current_status:
                     raise serializers.ValidationError({
                        "status": f"Impossible de modifier le statut d'une demande '{current_status}'."
                    })
                # Logique de transition des statuts
                status_order = {
                    'pending': 0, 'approved': 1, 'disbursed': 2, 'completed': 3,
                    'rejected': 98, 'cancelled': 99
                }
                if status_order.get(new_status, -1) < status_order.get(current_status, -1) and new_status not in ['rejected', 'cancelled']:
                    # Permettre le passage à rejected/cancelled depuis n'importe quel état avant completed
                    if not (new_status in ['rejected', 'cancelled'] and current_status not in ['completed', 'cancelled']):
                        raise serializers.ValidationError({
                            "status": f"Transition de statut invalide de '{current_status}' à '{new_status}'."
                        })
        return data

    def update(self, instance, validated_data):
        # Mettre à jour `approved_by` et `date_approved_rejected` si le statut change
        # et que l'utilisateur est un admin.
        new_status = validated_data.get('status', instance.status)

        if new_status != instance.status:
            # Assurez-vous que l'utilisateur effectuant la mise à jour est bien un admin
            # Cette logique sera également gérée par les permissions dans les vues,
            # mais c'est une sécurité supplémentaire.
            request_user = self.context.get('request').user
            if request_user and request_user.role == 'administrateur':
                if new_status in ['approved', 'rejected']:
                    instance.approved_by = request_user
                    instance.date_approved_rejected = timezone.now()
                elif instance.status in ['approved', 'rejected'] and new_status not in ['approved', 'rejected']:
                    # Si on revient d'un statut final (peu probable mais géré), reset
                    instance.approved_by = None
                    instance.date_approved_rejected = None
            else:
                # Empêcher un non-admin de changer le statut ou les champs admin
                raise serializers.ValidationError({"detail": "Seuls les administrateurs peuvent modifier le statut ou les commentaires."})

        # Si le statut passe à 'approved' et `amount_approved` n'est pas spécifié, utilisez `amount_requested`
        if new_status == 'approved' and validated_data.get('amount_approved') is None and instance.amount_approved is None:
            instance.amount_approved = instance.amount_requested

        return super().update(instance, validated_data)