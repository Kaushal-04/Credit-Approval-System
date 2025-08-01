from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from .models import Customer, Loan
from datetime import datetime
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

        if not all([first_name, last_name, phone_number, age, monthly_income]):
            return Response({"error": "All fields are required."}, status=400)

        if Customer.objects.filter(phone_number=phone_number).exists():
            return Response({"error": "Phone number already registered."}, status=400)

        try:
            age = int(age)
            monthly_income = int(monthly_income)
        except ValueError:
            return Response({"error": "Age and monthly_income must be integers."}, status=400)

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


@method_decorator(csrf_exempt, name='dispatch')
class CheckEligibilityView(APIView):
    def post(self, request):
        data = request.data

        customer_id = data.get('customer_id')
        loan_amount = data.get('loan_amount')
        interest_rate = data.get('interest_rate')
        tenure = data.get('tenure')

        if not all([customer_id, loan_amount, interest_rate, tenure]):
            return Response({"error": "All fields are required."}, status=400)

        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            return Response({"error": "Customer not found."}, status=404)

        customer_loans = Loan.objects.filter(customer=customer)
        current_year = datetime.now().year
        today = datetime.now().date()

        current_debt = sum(
            loan.loan_amount for loan in customer_loans if loan.end_date >= today
        )

        if current_debt > customer.approved_limit:
            credit_score = 0
        else:
            on_time_loan_count = sum(1 for loan in customer_loans if loan.emis_paid_on_time)
            total_loans = customer_loans.count()
            current_year_loans = sum(1 for loan in customer_loans if loan.start_date.year == current_year)
            approved_volume = sum(loan.loan_amount for loan in customer_loans)

            score = 0
            score += (on_time_loan_count / total_loans * 30) if total_loans else 0
            score += min(total_loans, 10) * 2
            score += min(current_year_loans, 5) * 3
            score += min(approved_volume / 1000000, 10) * 3
            credit_score = min(100, math.floor(score))

        try:
            r = float(interest_rate) / (12 * 100)
            emi = (
                float(loan_amount) * r * (1 + r) ** int(tenure)
            ) / ((1 + r) ** int(tenure) - 1)
        except Exception:
            return Response({"error": "Invalid loan or interest values."}, status=400)

        total_emis = sum(
            loan.monthly_installment for loan in customer_loans if loan.end_date >= today
        ) + emi

        if total_emis > 0.5 * customer.monthly_salary:
            return Response({
                "customer_id": customer.id,
                "approval": False,
                "interest_rate": float(interest_rate),
                "corrected_interest_rate": None,
                "tenure": tenure,
                "monthly_installment": round(emi, 2)
            }, status=200)

        corrected_interest_rate = float(interest_rate)
        approval = False

        if credit_score > 50:
            approval = True
        elif 50 >= credit_score > 30:
            approval = float(interest_rate) >= 12
            corrected_interest_rate = max(float(interest_rate), 12.0)
        elif 30 >= credit_score > 10:
            approval = float(interest_rate) >= 16
            corrected_interest_rate = max(float(interest_rate), 16.0)
        else:
            approval = False
            corrected_interest_rate = None

        return Response({
            "customer_id": customer.id,
            "approval": approval,
            "interest_rate": float(interest_rate),
            "corrected_interest_rate": corrected_interest_rate,
            "tenure": tenure,
            "monthly_installment": round(emi, 2)
        }, status=200)
