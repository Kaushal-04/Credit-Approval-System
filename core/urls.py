from django.urls import path
from core.views import RegisterCustomerView
from .views import RegisterCustomerView, CheckEligibilityView


urlpatterns = [
    path('register', RegisterCustomerView.as_view(), name='register'),
    path('check-eligibility', CheckEligibilityView.as_view()),
]
