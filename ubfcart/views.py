from django.db.models import Q
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from rest_framework.generics import (
    ListAPIView, RetrieveAPIView, CreateAPIView,
    UpdateAPIView, DestroyAPIView
)
from rest_framework import viewsets, permissions, authentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from . import serializers, models
from ubfcore import models as ubfcoremodels
from ubfquiz import models as ubfquizmodels
from student import models as studentmodels
from reward import models as rewardmodels
#from core.models import PersonalNotification as PN
#from core.serializers import PersonalNotification

import razorpay
from django.conf import settings

class BuyNowView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        context = {"request":request}
        type = request.data.get('type', None)
        id = request.data.get('id', None)
        if type is None or id is None:
            return Response({"message": "Invalid request"}, status=HTTP_400_BAD_REQUEST)
        try:
            student = studentmodels.Student.objects.get(user=self.request.user)
        except ObjectDoesNotExist:
            return Response("error",status=400)

        cart = models.UserCart.objects.create(student=student, ordered=False, single_product=True)

        if type.lower() == "pdf":
            pdf = get_object_or_404(ubfcoremodels.PDF, id=id)
            cart.pdfs.add(pdf)
        elif type.lower() == "mcq":
            mcq = get_object_or_404(ubfcoremodels.MCQ, id=id)
            cart.mcqs.add(mcq)
        elif type.lower() == 'summary':
            summary = get_object_or_404(ubfcoremodels.Summary, id=id)
            cart.summaries.add(summary)
        elif type.lower() == 'session':
            session = get_object_or_404(ubfcoremodels.Session, id=id)
            cart.sessions.add(session)
        elif type.lower() == 'test':
            quiz = get_object_or_404(ubfquizmodels.Quiz, id=id)
            cart.tests.add(quiz)
        else:
            return Response({"message": "Wrong Type"}, status=HTTP_400_BAD_REQUEST)
        cart.save()
        serializer = serializers.UserCartSerializer(cart, many=False, context=context)
        return Response(serializer.data)

class AddToCartView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        context = {"request":request}
        type = request.data.get('type', None)
        id = request.data.get('id', None)
        user = request.user
        if type is None or id is None:
            return Response({"message": "Invalid request"}, status=HTTP_400_BAD_REQUEST)
        try:
            student = studentmodels.Student.objects.get(user=self.request.user)
        except ObjectDoesNotExist:
            return Response("error",status=400)
        cart = models.UserCart.objects.filter(student=student, ordered=False, single_product=False)
        if cart.exists():
            cart = cart[0]
        else:
            cart = models.UserCart.objects.create(student=student, ordered=False, single_product=False)

        if type.lower() == "pdf":
            pdf = get_object_or_404(ubfcoremodels.PDF, id=id)
            cart.pdfs.add(pdf)
        elif type.lower() == "mcq":
            mcq = get_object_or_404(ubfcoremodels.MCQ, id=id)
            cart.mcqs.add(mcq)
        elif type.lower() == 'summary':
            summary = get_object_or_404(ubfcoremodels.Summary, id=id)
            cart.summaries.add(summary)
        elif type.lower() == 'session':
            session = get_object_or_404(ubfcoremodels.Session, id=id)
            cart.sessions.add(session)
        elif type.lower() == 'test':
            quiz = get_object_or_404(ubfquizmodels.Quiz, id=id)
            cart.tests.add(quiz)
        else:
            return Response({"message": "Wrong Type"}, status=HTTP_400_BAD_REQUEST)
        cart.save()
        serializer = serializers.UserCartSerializer(cart, many=False, context=context)
        return Response(serializer.data)

class RemoveFromCartView(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self, request, *args, **kwargs):
        context = {"request": request}
        type = request.data.get('type', None)
        id = request.data.get('id', None)
        user = request.user
        if type is None or id is None:
            return Response({"message": "Invalid request"}, status=HTTP_400_BAD_REQUEST)
        try:
            student = studentmodels.Student.objects.get(user=self.request.user)
        except ObjectDoesNotExist:
            return Response("error",status=400)
        cart = models.UserCart.objects.filter(student=student, ordered=False, single_product=False)
        if cart.exists():
            cart = cart[0]
        else:
            cart = models.UserCart.objects.create(student=student, ordered=False, single_product=False)

        if type.lower() == "pdf":
            pdf = get_object_or_404(ubfcoremodels.PDF, id=id)
            cart.pdfs.remove(pdf)
        elif type.lower() == "mcq":
            mcq = get_object_or_404(ubfcoremodels.MCQ, id=id)
            cart.mcqs.remove(mcq)
        elif type.lower() == 'summary':
            summary = get_object_or_404(ubfcoremodels.Summary, id=id)
            cart.summaries.remove(summary)
        elif type.lower() == 'session':
            session = get_object_or_404(ubfcoremodels.Session, id=id)
            cart.sessions.remove(session)
        elif type.lower() == 'test':
            quiz = get_object_or_404(ubfquizmodels.Quiz, id=id)
            cart.tests.remove(quiz)
        else:
            return Response({"message": "Wrong Type"}, status=HTTP_400_BAD_REQUEST)
        cart.save()
        if (cart.pdfs.all()).count()==0 and (cart.mcqs.all()).count()==0 and (cart.summaries.all()).count()==0 and (cart.sessions.all()).count()==0 and (cart.tests.all()).count()==0:
            cart.delete()
            return Response("Cart is Empty",status=200)
        serializer = serializers.UserCartSerializer(cart, many=False, context=context)
        return Response(serializer.data)

class AddToBookmarkView(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self, request, *args, **kwargs):
        context = {"request": request}
        type = request.data.get('type', None)
        id = request.data.get('id', None)
        user = request.user
        if type is None or id is None:
            return Response({"message": "Invalid request"}, status=HTTP_400_BAD_REQUEST)
        try:
            student = studentmodels.Student.objects.get(user=self.request.user)
        except ObjectDoesNotExist:
            return Response("error",status=400)
        bookmark, created = models.Bookmark.objects.get_or_create(student= student)
        if type.lower() == "pdf":
            pdf = get_object_or_404(ubfcoremodels.PDF, id=id)
            bookmark.pdfs.add(pdf)
        elif type.lower() == "mcq":
            mcq = get_object_or_404(ubfcoremodels.MCQ, id=id)
            bookmark.mcqs.add(mcq)
        elif type.lower() == 'summary':
            summary = get_object_or_404(ubfcoremodels.Summary, id=id)
            bookmark.summaries.add(summary)
        elif type.lower() == 'session':
            session = get_object_or_404(ubfcoremodels.Session, id=id)
            bookmark.sessions.add(session)
        elif type.lower() == 'test':
            quiz = get_object_or_404(ubfquizmodels.Quiz, id=id)
            bookmark.tests.add(quiz)
        else:
            return Response({"message": "Wrong Type"}, status=HTTP_400_BAD_REQUEST)
        bookmark.save()
        serializer = serializers.UserBookmarkSerializer(bookmark, many=False, context=context)
        return Response(serializer.data)

class RemoveFromBookmarkView(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self, request, *args, **kwargs):
        context = {"request": request}
        type = request.data.get('type', None)
        id = request.data.get('id', None)
        user = request.user
        if type is None or id is None:
            return Response({"message": "Invalid request"}, status=HTTP_400_BAD_REQUEST)
        try:
            student = studentmodels.Student.objects.get(user=self.request.user)
        except ObjectDoesNotExist:
            return Response("error",status=400)

        bookmark, created = models.Bookmark.objects.get_or_create(student=student)
        if type.lower() == "pdf":
            pdf = get_object_or_404(ubfcoremodels.PDF, id=id)
            bookmark.pdfs.remove(pdf)
        elif type.lower() == "mcq":
            mcq = get_object_or_404(ubfcoremodels.MCQ, id=id)
            bookmark.mcqs.remove(mcq)
        elif type.lower() == 'summary':
            summary = get_object_or_404(ubfcoremodels.Summary, id=id)
            bookmark.summaries.remove(summary)
        elif type.lower() == 'session':
            session = get_object_or_404(ubfcoremodels.Session, id=id)
            bookmark.sessions.remove(session)
        elif type.lower() == 'test':
            quiz = get_object_or_404(ubfquizmodels.Quiz, id=id)
            bookmark.tests.remove(quiz)
        else:
            return Response({"message": "Wrong Type"}, status=HTTP_400_BAD_REQUEST)
        bookmark.save()
        serializer = serializers.UserBookmarkSerializer(bookmark, many=False, context=context)
        return Response(serializer.data)

class AddToSaveForLaterView(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self, request, *args, **kwargs):
        context = {"request": request}
        type = request.data.get('type', None)
        id = request.data.get('id', None)
        user = request.user
        if type is None or id is None:
            return Response({"message": "Invalid request"}, status=HTTP_400_BAD_REQUEST)

        try:
            student = studentmodels.Student.objects.get(user=self.request.user)
        except ObjectDoesNotExist:
            return Response("error",status=400)

        saved,created = models.SaveForLater.objects.get_or_create(student=student)
        #cart,created = models.UserCart.objects.get_or_create(student=student)
        cart = models.UserCart.objects.get(id=request.data["cart id"])
        if type.lower() == "pdf":
            pdf = get_object_or_404(ubfcoremodels.PDF, id=id)
            cart.pdfs.remove(pdf)
            saved.pdfs.add(pdf)
        elif type.lower() == "mcq":
            mcq = get_object_or_404(ubfcoremodels.MCQ, id=id)
            cart.mcqs.remove(mcq)
            saved.mcqs.add(mcq)
        elif type.lower() == 'summary':
            summary = get_object_or_404(ubfcoremodels.Summary, id=id)
            cart.summaries.remove(summary)
            saved.summaries.add(summary)
        elif type.lower() == 'session':
            session = get_object_or_404(ubfcoremodels.Session, id=id)
            cart.sessions.remove(session)
            saved.sessions.add(session)
        elif type.lower() == 'test':
            quiz = get_object_or_404(ubfquizmodels.Quiz, id=id)
            cart.tests.remove(quiz)
            saved.tests.add(quiz)
        else:
            return Response({"message": "Wrong Type"}, status=HTTP_400_BAD_REQUEST)
        saved.save()
        serializer = serializers.UserSaveForLaterSerializer(saved, many=False, context=context)
        return Response(serializer.data)

class RemoveFromSavedForLaterView(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self, request, *args, **kwargs):
        context = {"request": request}
        type = request.data.get('type', None)
        id = request.data.get('id', None)
        user = request.user
        if type is None or id is None:
            return Response({"message": "Invalid request"}, status=HTTP_400_BAD_REQUEST)

        try:
            student = studentmodels.Student.objects.get(user=self.request.user)
        except ObjectDoesNotExist:
            return Response("error",status=400)

        saved, created = models.SaveForLater.objects.get_or_create(student=student)
        if type.lower() == "pdf":
            pdf = get_object_or_404(ubfcoremodels.PDF, id=id)
            saved.pdfs.remove(pdf)
        elif type.lower() == "mcq":
            mcq = get_object_or_404(ubfcoremodels.MCQ, id=id)
            saved.mcqs.remove(mcq)
        elif type.lower() == 'summary':
            summary = get_object_or_404(ubfcoremodels.Summary, id=id)
            saved.summaries.remove(summary)
        elif type.lower() == 'session':
            session = get_object_or_404(ubfcoremodels.Session, id=id)
            saved.sessions.remove(session)
        elif type.lower() == 'test':
            quiz = get_object_or_404(ubfquizmodels.Quiz, id=id)
            saved.tests.remove(quiz)
        else:
            return Response({"message": "Wrong Type"}, status=HTTP_400_BAD_REQUEST)
        saved.save()

        serializer = serializers.UserSaveForLaterSerializer(saved, many=False, context=context)
        return Response(serializer.data)

class UserOrdersView(ListAPIView):
    serializer_class = serializers.UserCartSerializer
    queryset = models.UserCart.objects.all()
    permission_classes = [IsAuthenticated,]

    def get_queryset(self):
        try:
            student = studentmodels.Student.objects.get(user=self.request.user)
        except ObjectDoesNotExist:
            return Response("error",status=400)
        queryset = models.UserCart.objects.filter(student=student, ordered=True)
        cart = self.request.query_params.get('cart', None)
        if cart is not None:
            queryset = queryset.filter(ordered=False)
        return queryset

class CartDetailView(RetrieveAPIView):
    serializer_class = serializers.UserCartSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        try:
            student = studentmodels.Student.objects.get(user=self.request.user)
        except ObjectDoesNotExist:
            return Response("error",status=400)
        cart = models.UserCart.objects.filter(student=student, ordered=False, single_product=False)
        if cart.exists():
            return cart[0]
        else:
            raise Http404("You do not have an active order")

class BookmarkDetailView(RetrieveAPIView):
    serializer_class = serializers.UserBookmarkSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        try:
            student = studentmodels.Student.objects.get(user=self.request.user)
        except ObjectDoesNotExist:
            return Response("error",status=400)
        try:
            bookmarked = models.Bookmark.objects.get(student=student)
            return bookmarked
        except ObjectDoesNotExist:
            raise Http404("You do not have anything Bookmarked")
            # return Response({"message": "You have Noting Bookmarked"}, status=HTTP_400_BAD_REQUEST)

class SaveForLaterDetailView(RetrieveAPIView):

    serializer_class = serializers.UserSaveForLaterSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        try:
            student = studentmodels.Student.objects.get(user=self.request.user)
        except ObjectDoesNotExist:
            return Response("error",status=400)
        try:
            save_for_later = models.SaveForLater.objects.get(student=student)
            return save_for_later
        except ObjectDoesNotExist:
            raise Http404("You do not have anything Saved for Later")
            # return Response({"message": "You have Noting Bookmarked"}, status=HTTP_400_BAD_REQUEST)

class ConfirmPaymentView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        try:
            student = studentmodels.Student.objects.get(user=self.request.user)
        except ObjectDoesNotExist:
            return Response("error",status=400)
        razorpay_payment_id = request.data.get('razorpay_payment_id', None)
        razorpay_order_id = request.data.get('razorpay_order_id', None)
        razorpay_signature = request.data.get('razorpay_signature', None)

        cart = get_object_or_404(models.UserCart, order_id = razorpay_order_id)

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
            if cart.single_product == True:
                cart.delete()
            raise Exception('Razorpay Signature Verification Failed')
        payment = models.Payment.objects.create(amount= cart.amount,order_id = razorpay_order_id, payment_id=razorpay_payment_id)
        payment.success = True
        payment.save()
        cart.ordered = True
        cart.payment = payment
        cart.ordered_date = timezone.now()
        cart.save()
        if cart.rewardcode is not None:
            code = rewardmodels.RewardCode.objects.get(id=cart.rewardcode.id)
            code.claimed=True
            code.save()
        ubfpayment = studentmodels.StudentUBFPayment.objects.create(title=str(student.name)+" has made purchase through ubf ",student=student,libraryBranch=student.library_branch,amount_paid=cart.amount//10)
        user_subscriptions, created = ubfcoremodels.UserSubscriptions.objects.get_or_create(student=student)
        try:
            user_subscriptions.pdfs.add(*cart.pdfs.all())
            user_subscriptions.mcqs.add(*cart.mcqs.all())
            user_subscriptions.summaries.add(*cart.summaries.all())
            user_subscriptions.sessions.add(*cart.sessions.all())
            user_subscriptions.tests.add(*cart.tests.all())
        except:
            return Response("issue here")
        user_subscriptions.save()
        # for i in cart.tests.all():
        #     if i.live ==True:
        #         #message =" has been purchased. Your quiz is scheduled on :"
        #         #pn =PN.objects.create(user=cart.user, quiz=i,message="")
        #         pn =PN(user=cart.user, quiz=i,message="")
        #         pn.save()


        return Response({"message": "Payment Successfull"}, status=HTTP_200_OK)

class PromocodeChecker(APIView):

    queryset = models.UserCart.objects.all()

    def post(self,request):
        cart = self.queryset.get(id=request.data["id"])

        try:
            student = studentmodels.Student.objects.get(user=self.request.user)
        except ObjectDoesNotExist:
            return Response("error",status=400)

        try:
            code = models.Promocode.objects.get(code=request.data["promocode"],active=True)
            instance = self.queryset.filter(student=student,promocode=code,ordered=True)
            if instance.count()>0:
                return Response({"error":"Promocode used already"},status=400)       
            cart.promocode = code
            cart.save()
            return Response("Promocode Added successfully",status=200)
        except ObjectDoesNotExist:
            #return Response({"error":"Invalid PromoCode"},status=400)
            pass
        #instance = self.queryset.filter(student=student,promocode=request.data["promocode"],ordered=True,codetype="reward")
        try:
            code = rewardmodels.RewardCode.objects.get(code=request.data["promocode"],student=student)
            instance = self.queryset.filter(student=student,rewardcode=code,ordered=True)
            if instance.count()>0:
                return Response({"error":"Reward code used already"},status=400)       
            cart.rewardcode = code          
            cart.save()
            return Response("Reward code Added successfully",status=200)        
        except ObjectDoesNotExist:
            #return Response({"error":"Invalid PromoCode"},status=400)
            pass
        return Response({"error":"Invalid PromoCode"},status=400)
        #return Response("Promocode Added successfully",status=200)

class PromocodeRemove(APIView):

    queryset = models.UserCart.objects.all()

    def post(self,request):
        
        cart = self.queryset.get(id=request.data["id"])
    
        try:
            student = studentmodels.Student.objects.get(user=self.request.user)
        except ObjectDoesNotExist:
            return Response("error",status=400)
        
        cart.rewardcode = None          
        cart.save()

        return Response({"Promocode removed"},status=400)
class PromocodeListAPI(ListAPIView):

    queryset = models.Promocode.objects.all()
    serializer_class = serializers.PromocodeSerializer
    permission_classes = [IsAuthenticated,]

    def get_queryset(self):

        queryset = self.queryset.filter(active=True)

        return queryset