from rest_framework import serializers
from .models import *

class RewardSerializer(serializers.ModelSerializer):

    class Meta:
        model = RewardSystem
        fields ='__all__'

class RewardCodeSerializer(serializers.ModelSerializer):

    class Meta:
        model = RewardCode
        fields = "__all__"