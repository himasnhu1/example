from django.shortcuts import render, get_object_or_404
from . import models, serializers
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
import datetime
from core import models as coremodels
from library import models as librarymodels
from student import models as studentmodels
from student import serializers as studentserializers
from django.conf import settings

from django.db.models import Q
from django.db.models import Avg, Count, Min, Sum
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import *  
from django.core.exceptions import ObjectDoesNotExist
import razorpay


class OwnerSubAPI(CreateAPIView):
    queryset = models.OwnerSubscriptionPlan.objects.all()
    serializer_class = serializers.OnwerSubscriptionSerializer
    permission_classes =[permissions.IsAuthenticated,]

    def create(self,request,*args,**kwargs):
        try:
            owner = models.Owner.objects.get(user=self.request.user)
        except ObjectDoesNotExist:
            return Response({"error":"User is not an Owner"},status=400)
        
        if owner.active_subscription is not None:

            if owner.active_subscription.title == "Free Tier":
                pass
            else:
                return Response({"error":"There is an active subscription on-going"},status=400)

        plan = models.OwnerSubPlan.objects.get(id=request.data["planid"])

        request.data["owner"]=owner.id
        request.data["title"]=plan.plan_name
        request.data["days"]=plan.days

        if 'branchesAllowed' not in request.data:
            request.data["branchesAllowed"] = 2
        else:
            amount = 0
            amount = plan.amount + ((int(request.data["branchesAllowed"])-2)*plan.extra*(plan.days//30))

            if amount != request.data["amount"]:
                return Response({"error":"Amount mismatch"},status=400)
   
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(serializer.data,status=200)
        

class OwnerSubViewAPI(RetrieveAPIView):
    queryset = models.OwnerSubscriptionPlan.objects.all()
    serializer_class = serializers.OnwerSubscriptionViewSerializer
    permission_classes =[permissions.IsAuthenticated,]

    def retrieve(self,request,*args,**kwargs):
        try:
            owner = models.Owner.objects.get(user=self.request.user)
        except ObjectDoesNotExist:
            return Response({"error":"User is not an Owner"},status=400)

        try:
            subscription = self.queryset.get(id = owner.active_subscription.id)
        except ObjectDoesNotExist:
            subscription = self.queryset.filter(owner=owner)
            subscription = subscription[0]
        
        serializer = self.serializer_class(subscription)

        return Response(serializer.data,status=200)

class ConfirmPaymentAPI(APIView):

    def post(self,request,*args,**kwargs):
        try:
            owner = models.Owner.objects.get(user=self.request.user)
        except ObjectDoesNotExist:
            return Response({"error":"User is not an Owner"},status=400)
        razorpay_payment_id = request.data.get('razorpay_payment_id', None)
        razorpay_order_id = request.data.get('razorpay_order_id', None)
        razorpay_signature = request.data.get('razorpay_signature', None)

        try:
            subscription = models.OwnerSubscriptionPlan.objects.get(owner=owner,order_id=razorpay_order_id)
        except ObjectDoesNotExist:
            return Response({"error":"Owner Subscription doesnt exist"},status=400)

        client = razorpay.Client(auth=(str(settings.RAZORPAY_KEY_ID), str(settings.RAZORPAY_KEY_SECRET)))
        # resp = client.order.fetch(razorpay_order_id)
        params_dict = {
            'razorpay_order_id': cart.order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature,
        }
        try:
            client.utility.verify_payment_signature(params_dict)
        except:
            raise Exception('Razorpay Signature Verification Failed')
        subscription.purchased = True
        subscription.active = True
        subscription.save()
        payment = models.Ownerpayment.objects.create(subscription=subscription,payment_id=razorpay_payment_id,amount_paid=subscription.amount)
        onwer.active_subscription=subscription
        owner.save()

        return Response({"message": "Payment Successfull"}, status=HTTP_200_OK)        

