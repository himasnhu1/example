from django.shortcuts import render, get_object_or_404
from .models import *
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
import datetime
from reward.serializers import *
from django.db.models import Q
from django.db.models import Avg, Count, Min, Sum
from rest_framework.response import Response
from rest_framework.views import APIView
from student import models as studentmodels
from ubfcart import models as ubfcartmodels
from django.core.exceptions import ObjectDoesNotExist
import uuid
from rest_framework.generics import *
class ConvertingpointsAPI(APIView):

    def post(self,request):
        try:
            student = studentmodels.Student.objects.get(user=self.request.user)
        except ObjectDoesNotExist:
            return Response("error",status=400)
        rewardsys = RewardSystem.objects.get(student=student)

        if rewardsys.points<200:
            return Response({"error":"Insuffiecent points"},status=400)

        if rewardsys.points >=200:
            counter=0
            while counter == 0:
                code = uuid.uuid4().hex[:9]
                try:
                    check = ubfcartmodels.Promocode.objects.get(code=code)
                except ObjectDoesNotExist:
                    break    
            newcode = RewardCode.objects.create(student=student,max_discount=50,code=code)
            rewardsys.points = rewardsys.points - 200
            rewardsys.claims = rewardsys.claims + 1
            rewardsys.save()
            return Response(newcode.code,status=200)

class rewardcodeList(ListAPIView):
    queryset = RewardCode.objects.all()
    serializer_class = RewardCodeSerializer
    permission_classes =[permissions.IsAuthenticated,]

    def list(self,request,*args,**kwargs):
    #def get_queryset(self):   
        try:
            student = studentmodels.Student.objects.get(user=self.request.user)
        except ObjectDoesNotExist:
            return Response("error",status=400)

        queryset =self.queryset.filter(student=student)

        claim = self.request.query_params.get('claim', None)
        if claim is not None:
            if claim == "false":
                queryset = queryset.filter(claimed=False)
            elif claim == "true":
                queryset = queryset.filter(claimed=True)
        else:
            queryset = queryset.filter(claimed=False)
        
        serializer = self.serializer_class(queryset,many=True)
        return Response(serializer.data,status=200)
    
class RewardSystemAPI(RetrieveAPIView):
    queryset = RewardSystem.objects.all()
    serializer_class = RewardSerializer
    permission_classes =[permissions.IsAuthenticated,]    

    def retrieve(self,request,*args,**kwargs):
        try:
            student = studentmodels.Student.objects.get(user=self.request.user)
        except ObjectDoesNotExist:
            return Response({"error":"User is not a student"},status=400)  

        queryset = self.queryset.get(student=student)

        serializer = self.serializer_class(queryset)

        return Response(serializer.data,status=200)

class ReferralcodeAPI(APIView):

    permission_classes = [permissions.AllowAny]

    def post(self,request):
        try:
            student = studentmodels.Student.objects.get(referral_code=request.data["referralcode"])
        except ObjectDoesNotExist:
            return Response({"error":"Referral code invalid"},status=400)
        
        sys = RewardSystem.objects.get(student=student)

        sys.points = sys.points + 50
        sys.totalReferral = sys.totalReferral + 1

        sys.save()

        return Response({"Successful"},status=200)


