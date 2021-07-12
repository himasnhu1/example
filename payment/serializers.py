from rest_framework import serializers
from .models import *

class StudentPaymentOrderSerializer(serializers.ModelSerializer):

    class Meta:
        models = Studentpaymentorder
        fields ='__all__'