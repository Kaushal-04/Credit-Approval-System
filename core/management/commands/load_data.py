import pandas as pd
from django.core.management.base import BaseCommand
from core.models import Customer, Loan
from datetime import datetime
import os

class Command(BaseCommand):
    help = 'Load customer and loan data from Excel files'

    def handle(self, *args, **kwargs):
        base_path = os.path.join(os.getcwd(), 'data')

        # Load customer data
        customer_file = os.path.join(base_path, 'customer_data.xlsx')
        df_customers = pd.read_excel(customer_file)

        for _, row in df_customers.iterrows():
            Customer.objects.update_or_create(
                id=row['customer_id'],
                defaults={
                    'first_name': row['first_name'],
                    'last_name': row['last_name'],
                    'age': row['age'],
                    'phone_number': row['phone_number'],
                    'monthly_salary': row['monthly_salary'],
                    'approved_limit': row['approved_limit'],
                    'current_debt': 0.0
                }
            )
        self.stdout.write(self.style.SUCCESS("Customer data loaded successfully."))

        # Load loan data
        loan_file = os.path.join(base_path, 'loan_data.xlsx')
        df_loans = pd.read_excel(loan_file)

        for _, row in df_loans.iterrows():
            customer = Customer.objects.get(id=row['customer_id'])
            Loan.objects.update_or_create(
                id=row['loan_id'],
                defaults={
                    'customer': customer,
                    'loan_amount': row['loan_amount'],
                    'tenure': row['tenure'],
                    'interest_rate': row['interest_rate'],
                    'monthly_payment': row['monthly_payment'],
                    'emis_paid_on_time': row['emis_paid_on_time'],
                    'date_of_approval': pd.to_datetime(row['date_of_approval']).date()
                        if not pd.isnull(row['date_of_approval']) else None,
                    'end_date': pd.to_datetime(row['end_date']).date()
                        if not pd.isnull(row['end_date']) else None
                }
            )
        self.stdout.write(self.style.SUCCESS("Loan data loaded successfully."))
