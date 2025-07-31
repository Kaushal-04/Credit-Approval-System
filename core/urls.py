from django.urls import path
from core.views import RegisterCustomerView

urlpatterns = [
    path('register', RegisterCustomerView.as_view(), name='register'),
]
