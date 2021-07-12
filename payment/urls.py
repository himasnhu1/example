from django.urls import path, include
from .views import *

urlpatterns = [

    path('student/',OrderIdGeneratingAPI.as_view()),
    path('student/confirm-payment/',PaymentOrderVerificationAPI.as_view()),

]
