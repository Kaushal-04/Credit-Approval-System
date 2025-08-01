from django.urls import path
from core.views import RegisterCustomerView
from .views import RegisterCustomerView, CheckEligibilityView, CreateLoanView, ViewLoanDetail, ViewCustomerLoansView


urlpatterns = [
    path('register', RegisterCustomerView.as_view(), name='register'),
    path('check-eligibility', CheckEligibilityView.as_view()),
    path('create-loan', CreateLoanView.as_view()),
    path('view-loan/<int:loan_id>', ViewLoanDetail.as_view(), name='view-loan'),
    path('view-loans/<int:customer_id>', ViewCustomerLoansView.as_view(), name='view-loans'),
]
