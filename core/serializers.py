from rest_framework import serializers
from core.models import Customer

class RegisterCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'age', 'monthly_salary', 'phone_number']

    def create(self, validated_data):
        validated_data.pop('id', None)  # Ignore user-supplied ID during registration

        salary = validated_data['monthly_salary']
        approved_limit = round((36 * salary) / 100000) * 100000

        customer = Customer.objects.create(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            age=validated_data['age'],
            phone_number=validated_data['phone_number'],
            monthly_salary=salary,
            approved_limit=approved_limit,
            current_debt=0.0
        )
        return customer

