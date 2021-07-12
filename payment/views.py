from django.shortcuts import render
from . import models
from . import serializers
from rest_framework import viewsets, status, permissions
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_list_or_404, get_object_or_404
# from webapi
import datetime
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q,Sum
from rest_framework.views import APIView
import razorpay
from django.conf import settings

from student import models as studentmodels
from django.core.exceptions import ObjectDoesNotExist

class OrderIdGeneratingAPI(APIView):

    permission_classes =[IsAuthenticated,]

    def post(self,request):
        try:
            student = studentmodels.Student.objects.get(user=self.request.user)
        except ObjectDoesNotExist:
            return Response({"error":"User is not a student. please check again"},status=400)
        if student.active_subscription == None:
            return Response({"error":"No Active Subscription. please check again"},status=400)
        payments = studentmodels.StudentPayment.objects.filter(purchased_subscription=student.active_subscription).aggregate(Sum('amount_paid'))
        payments = payments['amount_paid__sum']
        if payments:
            due = student.active_subscription.total_amount - payments
        else:
            due=student.active_subscription.total_amount
        if due>0:
            if int(request.data["amount"])>due:
                return Response({"error":"Please Enter Amount Less Than Or Equal To Due"},status=400)
        else:
            return Response({"error":"No Dues Pending"},status=400)
        obj = models.Studentpaymentorder.objects.create(student=student,amount=int(request.data["amount"]))
        data = {
            "amount" : obj.amount*100,
            "currency" : 'INR',
            "receipt" : str(obj.id),
            "payment_capture" : '1',
        }
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        order_id = client.order.create(data = data)
        obj.order_id = order_id["id"]
        obj.save()

        return Response({"order_id":order_id,"student":{"name":student.name}},status=200)

class PaymentOrderVerificationAPI(APIView):

    permission_classes = [IsAuthenticated,]

    def post(self,request):

        try:
            student = studentmodels.Student.objects.get(user=self.request.user)
        except ObjectDoesNotExist:
            return Response({"error":"User is not a student. please check again"},status=400)
        
        orders = models.Studentpaymentorder.objects.filter(student=student,payment_id=None).order_by('-id')
        order = orders[0]
        razorpay_payment_id = request.data.get('razorpay_payment_id', None)
        razorpay_order_id = request.data.get('razorpay_order_id', None)
        razorpay_signature = request.data.get('razorpay_signature', None)

        payment = models.Studentpaymentorder.objects.get(student=student,order_id=request.data["razorpay_order_id"])

        client = razorpay.Client(auth=(str(settings.RAZORPAY_KEY_ID), str(settings.RAZORPAY_KEY_SECRET)))
        # resp = client.order.fetch(razorpay_order_id)
        params_dict = {
            'razorpay_order_id': order.order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature,
        }
        try:
            client.utility.verify_payment_signature(params_dict)
        except:
            raise Exception('Razorpay Signature Verification Failed')
        payment.success = True
        payment.payment_id = request.data["razorpay_payment_id"]
        payment.save()

        title = "Payment made of Rs"+str(payment.amount)
        studentpay = studentmodels.StudentPayment.objects.create(title=title,purchased_subscription=student.active_subscription,amount_paid=payment.amount,payment_mode='Paytm')

        return Response({"Message":"Payment successful"},status=200)