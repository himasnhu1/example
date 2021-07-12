from django.shortcuts import render, get_object_or_404, get_list_or_404
from . import models, serializers
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView, ListAPIView,CreateAPIView
from rest_framework.decorators import api_view, schema
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail.message import EmailMessage

from rest_auth.registration.views import SocialLoginView
#from quiz import models as quizmodels
#from cart import models as cartmodels
#from cart import serializers as cartserializer
from student import models as studentmodels
import operator



from django.db.models import Q
class Subscriptions():
    def __init__(self, pdfs, mcqs, summaries, sessions, tests):
        self.pdfs = pdfs
        self.mcqs = mcqs
        self.summaries = summaries
        self.sessions = sessions
        self.tests = tests

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = models.Category.objects.all()
    serializer_class = serializers.CategorySerializer
    http_method_names = ['get','options','head']

    def get_permissions(self):
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]

class SubCategoryViewSet(viewsets.ModelViewSet):
    queryset = models.SubCategory.objects.all()
    serializer_class = serializers.SubCategorySerializer
    http_method_names = ['get','options','head']

    def get_permissions(self):
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]

class PDFSerializer(viewsets.ModelViewSet):
    queryset = models.PDF.objects.all()
    serializer_class = serializers.PDFSerializer
    http_method_names = ['get','options','head']

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = [permissions.AllowAny]
        elif self.action == 'retrieve':
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        queryset = models.PDF.objects.all()

        subcategory = self.request.query_params.get('subcategory', None)
        if subcategory is not None:
            queryset = queryset.filter(sub_category__name__iexact =subcategory)

        price = self.request.query_params.get('price', None)
        if price is not None:
            queryset = queryset.filter(price__exact = int(price))

        search = self.request.query_params.get('search', None)
        if search is not None:
            queryset = queryset.filter(name__icontains = search)
        return queryset.order_by("-id")

    def retrieve(self, request, pk=None, *args, **kwargs):
        serializer_context = {
            'request': request,
        }
        queryset = models.PDF.objects.all()
        pdf = get_object_or_404(queryset, pk=pk)
        serializer = serializers.PDFListSerializer(pdf, context=serializer_context)
        return Response(serializer.data)

    def list(self,request,*args,**kwargs):
        queryset = self.get_queryset()
        serializer_context = {
            'request': request,
        }
        serializer = serializers.PDFListSerializer(queryset,many=True, context=serializer_context)
        return Response(serializer.data)

class ArticleViewSet(viewsets.ModelViewSet):
    queryset = models.Article.objects.all().order_by("-id")
    serializer_class = serializers.ArticleSerializer
    http_method_names = ['get','options','head']

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]
class MCQSerializer(viewsets.ModelViewSet):
    queryset = models.MCQ.objects.all()
    serializer_class = serializers.MCQSerializer
    http_method_names = ['get','options','head']

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = [permissions.AllowAny]
        elif self.action == 'retrieve':
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        queryset = models.MCQ.objects.all()

        subcategory = self.request.query_params.get('subcategory', None)
        if subcategory is not None:
            queryset = queryset.filter(sub_category__name__iexact =subcategory)

        price = self.request.query_params.get('price', None)
        if price is not None:
            queryset = queryset.filter(price__exact = int(price))

        search = self.request.query_params.get('search', None)
        if search is not None:
            queryset = queryset.filter(name__icontains = search)
        return queryset.order_by("-id")

    def retrieve(self, request, pk=None, *args, **kwargs):
        serializer_context = {
            'request': request,
        }
        queryset = models.MCQ.objects.all()
        mcq = get_object_or_404(queryset, pk=pk)
        try:
            print(self.request.user)
            student = Student.objects.get(user=self.request.user)

        except ObjectDoesNotExist:
            return Response("error student not found",status=400)
        subscribed = get_object_or_404(models.UserSubscriptions, student=student)
        if (mcq in subscribed.mcqs.all()) or mcq.price < 1:
            serializer = serializers.MCQSerializer(mcq, context=serializer_context)
            return Response(serializer.data)
        else:
            return Response({"message": "MCQ Not Purchased"}, status=HTTP_400_BAD_REQUEST)
    
    def list(self,request,*args,**kwargs):
        queryset = self.get_queryset()
        serializer_context = {
            'request': request,
        }
        serializer = serializers.MCQListSerializer(queryset,many=True, context=serializer_context)
        return Response(serializer.data)


class SummarySerializer(viewsets.ModelViewSet):
    queryset = models.Summary.objects.all()
    serializer_class = serializers.SummarySerializer
    http_method_names = ['get','options','head']

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = [permissions.AllowAny]
        elif self.action == 'retrieve':
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        queryset = models.Summary.objects.all()

        subcategory = self.request.query_params.get('subcategory', None)
        if subcategory is not None:
            queryset = queryset.filter(sub_category__name__iexact =subcategory)

        price = self.request.query_params.get('price', None)
        if price is not None:
            queryset = queryset.filter(price__exact = int(price))

        search = self.request.query_params.get('search', None)
        if search is not None:
            queryset = queryset.filter(name__icontains = search)
        return queryset.order_by("-id")

    def retrieve(self, request, pk=None, *args, **kwargs):
        serializer_context = {
            'request': request,
        }
        queryset = models.Summary.objects.all()
        summary = get_object_or_404(queryset, pk=pk)
        try:
            print(self.request.user)
            student = Student.objects.get(user=self.request.user)

        except ObjectDoesNotExist:
            return Response("error student not found",status=400)

        subscribed = get_object_or_404(models.UserSubscriptions, student = student)
        if (summary in subscribed.summaries.all()) or summary.price < 1:
            serializer = serializers.SummarySerializer(summary, context=serializer_context)
            return Response(serializer.data)
        else:
            return Response({"message": "Summary Not Purchased"}, status=HTTP_400_BAD_REQUEST)

    def list(self,request,*args,**kwargs):
        queryset = self.get_queryset()
        serializer_context = {
            'request': request,
        }
        serializer = serializers.SummaryListSerializer(queryset,many=True, context=serializer_context)
        return Response(serializer.data)

class SessionSerializer(viewsets.ModelViewSet):
    queryset = models.Session.objects.all()
    serializer_class = serializers.SessionSerializer
    http_method_names = ['get','options','head']

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = [permissions.AllowAny]
        elif self.action == 'retrieve':
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        queryset = models.Session.objects.all()

        price = self.request.query_params.get('price', None)
        if price is not None:
            queryset = queryset.filter(price__exact = int(price))

        search = self.request.query_params.get('search', None)
        if search is not None:
            queryset = queryset.filter(name__icontains = search)
        return queryset

    def retrieve(self, request, pk=None, *args, **kwargs):
        serializer_context = {
            'request': request,
        }
        queryset = models.Session.objects.all()
        session = get_object_or_404(queryset, pk=pk)
        try:
            print(self.request.user)
            student = Student.objects.get(user=self.request.user)

        except ObjectDoesNotExist:
            return Response("error student not found",status=400)

        subscribed = get_object_or_404(models.UserSubscriptions, student=student)
        if (session in subscribed.sessions.all()) or session.price < 1:
            serializer = serializers.SessionSerializer(session, context=serializer_context)
            return Response(serializer.data)
        else:
            return Response({"message": "Session Not Purchased"}, status=HTTP_400_BAD_REQUEST)

    def list(self,request,*args,**kwargs):
        queryset = self.get_queryset()
        serializer_context = {
            'request': request,
        }
        serializer = serializers.SessionListSerializer(queryset,many=True, context=serializer_context)
        return Response(serializer.data)

class UserSubscriptionsSerializer(viewsets.ModelViewSet):
    queryset = models.UserSubscriptions.objects.all()
    serializer_class = serializers.UserSubscriptionsSerializer
    http_method_names = ['get','options','head']

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]

    def list(self, request, *args, **kwargs):
        user = request.user
        serializer_context = {
            'request': request,
        }
        queryset = models.UserSubscriptions.objects.all()
        try:
            print(self.request.user)
            student = studentmodels.Student.objects.get(user=self.request.user)

        except ObjectDoesNotExist:
            return Response("error student not found",status=400)
        user_subscription = get_object_or_404(queryset, student=student)
        serializer = serializers.UserSubscriptionsSerializer(user_subscription, many=False, context=serializer_context)
        return Response(serializer.data)

class SearchSubscriptionsView(APIView):

    def get(self, request):
        pdfs = models.PDF.objects.all()
        mcqs = models.MCQ.objects.all()
        summaries = models.Summary.objects.all()
        sessions = models.Session.objects.all()
        #tests = quizmodels.Quiz.objects.all()

        search = self.request.query_params.get('search', None)
        if search is not None:
            pdfs = pdfs.filter(name__icontains = search)
            mcqs = mcqs.filter(Q(name__icontains = search) | Q(description__icontains = search))
            summaries = summaries.filter(Q(name__icontains = search) | Q(description__icontains = search))
            sessions = sessions.filter(name__icontains = search)
            #tests = tests.filter(Q(name__icontains = search)| Q(description__icontains = search))

        subscriptions = Subscriptions(pdfs, mcqs, summaries, sessions, tests)
        context ={
            "request":request
        }
        data = serializers.SearchSerializer(subscriptions,context=context).data
        return Response(data)

class Notification(ListAPIView):

    queryset = models.GeneralNotification.objects.all()
    serializer_class = serializers.GeneralNotificationSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = self.queryset.filter(rollOut=True)
        return queryset.order_by('-timestamp')

# class PersonalNotification(ListAPIView):

#     queryset = models.PersonalNotification.objects.all()
#     serializer_class = serializers.Personalnotif
#     permission_classes = [permissions.IsAuthenticated]

#     def get_queryset(self):
#         queryset = self.queryset.filter(user=self.request.user)
#         #queryset2 = models.GeneralNotification.objects.filter(rollOut=True)
#         #notif_list = chain(queryset, queryset2)
#         # return queryset.order_by('-timestamp')
#         #ordered = sorted(notif_list, key=operator.attrgetter('-timestamp'))
#         return queryset

# class PromocodeAPI(CreateAPIView):
#     queryset = models.PromoCode.objects.all()
#     serializer_class = serializers.PromoUser
#     permission_classes = [permissions.IsAuthenticated]

#     def create(self,request,*args,**kwargs):
#         try:
#             code = self.queryset.get(code=request.data["code"],active=True)
#         except ObjectDoesNotExist:
#             return Response("Invalid Code. Please Enter A Valid Code")
        
#         obj,created = models.UserCode.objects.get_or_create(user=request.user,code=code)

#         if created:
#             cart = cartmodels.UserCart.objects.get(id=request.data["cart_id"])
#             cart.promocode = code
#             cart.save()
#             #cart = cartmodels.UserCart.objects.get(id=request.data["cart_id"])
#             #serializer = cartserializer.UserCartSerializer(cart)
#             return Response("Added Successfully",status=200)
        
#         if obj:
#             return Response("User has alreadys used the promo code")

# class PromoCodeViewAPI(ListAPIView):
#     queryset = models.PromoCode.objects.all()
#     serializer_class = serializers.PromoCode
#     #permission_classes = [permissions.IsAuthenticated]

#     def get_queryset(self):
#         queryset = self.queryset.filter(active=True)

#         return queryset.order_by('-timestamp')

    

