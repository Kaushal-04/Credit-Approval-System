from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from .models import Customer
import math

@method_decorator(csrf_exempt, name='dispatch')
class RegisterCustomerView(APIView):
    def post(self, request):
        data = request.data

        first_name = data.get('first_name')
        last_name = data.get('last_name')
        phone_number = data.get('phone_number')
        age = data.get('age')
        monthly_income = data.get('monthly_income')

        # Validate required fields
        if not all([first_name, last_name, phone_number, age, monthly_income]):
            return Response({"error": "All fields are required."}, status=400)

        # Check for duplicate phone number
        if Customer.objects.filter(phone_number=phone_number).exists():
            return Response({"error": "Phone number already registered."}, status=400)

        try:
            age = int(age)
            monthly_income = int(monthly_income)
        except ValueError:
            return Response({"error": "Age and monthly_income must be integers."}, status=400)

        # Calculate approved limit rounded to nearest lakh
        approved_limit = round(36 * monthly_income / 100000) * 100000

        try:
            with transaction.atomic():
                customer = Customer.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    age=age,
                    phone_number=phone_number,
                    monthly_salary=monthly_income,
                    approved_limit=approved_limit,
                    current_debt=0
                )

            return Response({
                "customer_id": customer.id,
                "name": f"{customer.first_name} {customer.last_name}",
                "age": customer.age,
                "monthly_income": customer.monthly_salary,
                "approved_limit": customer.approved_limit,
                "phone_number": customer.phone_number
            }, status=201)

        except Exception as e:
            return Response({"error": str(e)}, status=500)
