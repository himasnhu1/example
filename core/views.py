from django.shortcuts import render
from . import models
from . import models, serializers
from rest_framework import viewsets, status, permissions
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_list_or_404, get_object_or_404
# from webapi
import datetime
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework.views import APIView
from django.core.mail import EmailMessage
from django.core.mail import EmailMultiAlternatives
from django.template import Context
from django.template.loader import render_to_string
from django.utils.html import strip_tags

import uuid
from django.core.files.storage import default_storage
# Create your views here.


class UserSerializerAPIViewSet(viewsets.ModelViewSet):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = [permissions.IsAuthenticated,]
    http_method_names = ['post', 'head','options']

 
    # @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser|IsOwner])
    # def set_password(self, request, pk=None):
    #     user = self.get_object()
    #     serializer = PasswordSerializer(data=request.data)
    #     if serializer.is_valid():
    #         user.set_password(serializer.data['password'])
    #         user.save()
    #         return Response({'status': 'password set'})
    #     else:
    #         return Response(serializer.errors,
    #                         status=status.HTTP_400_BAD_REQUEST)
    #
    # @action(detail=False)
    # def recent_users(self, request):
    #     recent_users = User.objects.all().order_by('-last_login')
    #
    #     page = self.paginate_queryset(recent_users)
    #     if page is not None:
    #         serializer = self.get_serializer(page, many=True)
    #         return self.get_paginated_response(serializer.data)
    #
    #     serializer = self.get_serializer(recent_users, many=True)
    #     return Response(serializer.data)

    def get_permissions(self):
        if self.action == 'post':
            permission_classes = [IsAuthenticated]
            # user = self.queryset.get(id=self.request.user.id)
            # if user.isadmin:
            #     permission_classes = [IsAuthenticated]
            # else:
            #     return Response("error",status=401)
        else:
            permission_classes = [IsAdminUser]
            # permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

class DeviceViewSet(viewsets.ModelViewSet):
    queryset = models.MyDevice.objects.all()
    serializer_class = serializers.DeviceSerializer
    permission_classes = [IsAuthenticated,]

class HigherEducationAPIViewSet(viewsets.ModelViewSet):
    queryset = models.HigherEducation.objects.all()
    serializer_class = serializers.HigherEducationSerializer
    permission_classes = [IsAuthenticated,]
    # def get_permissions(self):
    #     if self.action == 'list':
    #         permission_classes = [IsAuthenticated]
    #     else:
    #         permission_classes = [IsAdminUser]
    #     return [permission() for permission in permission_classes]

class ExamsPreparingForAPIViewSet(viewsets.ModelViewSet):
    queryset = models.ExamsPreparingFor.objects.all()
    serializer_class = serializers.ExamsPreparingForSerializer
    permission_classes = [IsAuthenticated,]

    # def get_permissions(self):
    #     if self.action == 'list':
    #         permission_classes = [IsAuthenticated]
    #     else:
    #         permission_classes = [IsAdminUser]
    #     return [permission() for permission in permission_classes]


class OpeningDaysAPIViewSet(viewsets.ModelViewSet):
    queryset = models.OpeningDays.objects.all()
    serializer_class = serializers.OpeningDaysSerializer
    permission_classes = [IsAuthenticated,]
    # def get_permissions(self):
    #     if self.action == 'list':
    #         permission_classes = [IsAuthenticated]
    #     else:
    #         permission_classes = [IsAdminUser]
    #     return [permission() for permission in permission_classes]


class TimeSlotAPIViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.TimeSlotSerializer
    permission_classes = [IsAuthenticated,]
    http_method_names = ['post', 'get','head','options']

    def get_queryset(self):
        queryset = models.TimeSlot.objects.filter(active=True)
        return queryset

    # def list(self, request, *args, **kwargs):
    #     user = request.user or request.auth
    #     serializer_context = {
    #         'request': request,
    #     }
    #     if user.is_admin:
    #         queryset = models.TimeSlot.objects.all()
    #         serializer = serializers.TimeSlotSerializer(queryset, many=True, context=serializer_context)
    #         return Response(serializer.data)
    #     else:
    #         queryset = models.TimeSlot.objects.filter(active=True)
    #         serializer = serializers.TimeSlotSerializer(queryset, many=True, context=serializer_context)
    #         return Response(serializer.data)
    #
    # def retrieve(self, request, pk=None, *args, **kwargs):
    #     serializer_context = {
    #         'request': request,
    #     }
    #     queryset = models.TimeSlot.objects.all()
    #     time_slot = get_object_or_404(queryset, pk=pk)
    #     serializer = serializers.TimeSlotSerializer(time_slot, context=serializer_context)
    #     return Response(serializer.data)
    #
    # def update(self, request, *args, **kwargs):
    #     partial = kwargs.pop('partial', False)
    #     instance = self.get_object()
    #     serializer = self.get_serializer(instance, data=request.data, partial=partial)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_update(serializer)
    #     return Response(serializer.data)
    #
    # def create(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_create(serializer)
    #     headers = self.get_success_headers(serializer.data)
    #     return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    #
    # def destroy(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     self.perform_destroy(instance)
    #     return Response(status=status.HTTP_204_NO_CONTENT)
    #
    # def partial_update(self, request, *args, **kwargs):
    #     kwargs['partial'] = True
    #     return self.update(request, *args, **kwargs)

    # def get_permissions(self):
    #     if self.action == 'list':
    #         permission_classes = [IsAuthenticated]
    #     else:
    #         permission_classes = [IsAdminUser]
    #     return [permission() for permission in permission_classes]


class SubscriptionPlanAPIViewSet(viewsets.ModelViewSet):
    queryset = models.SubscriptionPlan.objects.all()
    serializer_class = serializers.SubscriptionPlanSerializer
    permission_classes = [IsAuthenticated,]
    # def get_permissions(self):
    #     if self.action == 'list':
    #         permission_classes = [IsAuthenticated]
    #     else:
    #         permission_classes = [IsAdminUser]
    #     return [permission() for permission in permission_classes]


class SubscriptionPaymentAPIViewSet(viewsets.ModelViewSet):
    queryset = models.SubscriptionPayment.objects.all()
    serializer_class = serializers.SubscriptionPaymentSerializer
    permission_classes = [IsAuthenticated,]
    # def get_permissions(self):
    #     if self.action == 'list':
    #         permission_classes = [IsAuthenticated]
    #     else:
    #         permission_classes = [IsAdminUser]
    #     return [permission() for permission in permission_classes]


class IncidentAPIViewSet(viewsets.ModelViewSet):
    queryset = models.Incident.objects.all()
    serializer_class = serializers.IncidentSerializer
    permission_classes = [permissions.IsAuthenticated, ]
    http_method_names = ['post', 'head','options']

    # def get_permissions(self):
    #     if self.action == 'create' or self.action == 'list':
    #         permission_classes = [IsAuthenticated]
    #     else:
    #         permission_classes = [IsAdminUser]
    #     return [permission() for permission in permission_classes]
    def create(self,request,*args,**kwargs):

        request.data["ticket"]=uuid.uuid4().hex[:25]
        request.data["active"]=True
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        
        incident = self.queryset.get(id=serializer.data["id"])

        html_content = render_to_string('core/incident.html',{"ticket":request.data["ticket"],"user":incident.user})
        text_content = strip_tags(html_content)
        email = EmailMultiAlternatives('Incident Reported', text_content,'testingserver.12307@gmail.com',["yashch1998@gmail.com",])
        email.attach_alternative(html_content, "text/html")

        docfile = default_storage.open(incident.image.name, 'r')
        email.attach(docfile.name, docfile.read())

        email.send()

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class FeedbackAPIViewSet(viewsets.ModelViewSet):
    queryset = models.Feedback.objects.all()
    serializer_class = serializers.FeedbackSerializer
    # permission_classes = [permissions.IsAuthenticated, ]

    # def get_permissions(self):
    #     if self.action == 'create':
    #         permission_classes = [IsAuthenticated]
    #     else:
    #         permission_classes = [IsAdminUser]
    #     return [permission() for permission in permission_classes]


class FAQAPIViewSet(viewsets.ModelViewSet):
    queryset = models.FAQ.objects.all()
    serializer_class = serializers.FAQSerializer
    http_method_names = ['get', 'head','options']

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        queryset = models.FAQ.objects.all()

        search = self.request.query_params.get('search', None)
        if search is not None:
            queryset = queryset.filter(Q(question__icontains=search) | Q(answer__icontains=search))
        type = self.request.query_params.get('user_type', None)
        if type is not None:
            queryset = queryset.filter(user_type=type)

        return queryset

class NotificationAPIViewSet(viewsets.ModelViewSet):
    queryset = models.Notification.objects.all()
    serializer_class = serializers.NotificationSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def get_queryset(self):
        # queryset = models.FAQ.objects.all()

        # user = self.request.query_params.get('user', None)
        # if user is not None:
        #     queryset = self.queryset.filter(user__id = int(user))

        user = self.request.user
        if user is not None:
            queryset = self.queryset.filter(user__id = user.id)

        search = self.request.query_params.get('search', None)
        if search is not None:
            queryset = self.queryset.filter(Q(subject__icontains=search) | Q(message__icontains=search))

        return queryset

class CurrentAffairCategoryAPIViewSet(viewsets.ModelViewSet):
    queryset = models.CurrentAffairCategory.objects.all()
    serializer_class = serializers.CurrentAffairCategorySerializer

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]


class CurrentAffairAPIViewSet(viewsets.ModelViewSet):
    queryset = models.CurrentAffair.objects.all()
    serializer_class = serializers.CurrentAffairSerializer

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        queryset = models.CurrentAffair.objects.all()

        category = self.request.query_params.get('category', None)
        if category is not None:
            queryset = queryset.filter(category__id = int(category))

        search = self.request.query_params.get('search', None)
        if search is not None:
            queryset = queryset.filter(Q(title__icontains=search) | Q(description__icontains=search))

        return queryset

class CurrentAffairImageAPIViewSet(viewsets.ModelViewSet):
    queryset = models.CurrentAffairImage.objects.all()
    serializer_class = serializers.CurrentAffairImageSerializer

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

class AmmenitiesAPIViewSet(viewsets.ModelViewSet):
    queryset = models.Ammenity.objects.all()
    serializer_class = serializers.AmmenitiesSerializer
    permission_classes = [IsAuthenticated,]
    http_method_names = ['post', 'get', 'head','options']
    # def get_permissions(self):
    #     if self.action == 'list':
    #         permission_classes = [IsAuthenticated]
    #     else:
    #         permission_classes = [IsAdminUser]
    #     return [permission() for permission in permission_classes]

class UserChangedPasswordAPI(APIView):
    permission_classes = [permissions.IsAuthenticated, ]
    queryset = models.User.objects.all()

    def patch(self,request):
        user = self.queryset.get(id=request.user.id)
        if request.data['passwordchanged'] == True or request.data['passwordchanged'] == "true":
            user.passwordchanged = True
            user.save()
            return Response("Updated Successfully",status=200)
        return Response("unknown error",status=400)

class EnquiryEmailAPI(APIView):
    #permission_classes = [permissions.IsAuthenticated, ]

    def post(self,request):
        
        mail=request.data["email"]
        name = request.data["name"]
        enquiry = request.data["enquiry"]
        msg = 'Hello my name is '+str(name)+'\n\n My enquiry is:\n\n'+str(enquiry)+'\n\nMy Mail id is:'+str(mail)+'\n\nThank You,\n\n'+str(name)
        email = EmailMessage(subject='Invoice',body=msg,from_email='testingserver.12307@gmail.com',to=['yashvikaschodancar@power2create.in',])

        email.send()
        return Response("email sent successfully",status=200)







