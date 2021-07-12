from django.urls import path, include
from .enquiryapi import *
from .views import *

urlpatterns = [
    path('api/owner/student-invoice/send/', InvoiceEmailAPI.as_view()),
    path('api/owner/owner-invoice/send/',OwnerInvoiceEmailAPI.as_view()),
    path('api/owner/data/<int:pk>/',OwnerAPIEdit.as_view()),
 
]