from django.shortcuts import render, get_object_or_404
from . import models, serializers
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
import datetime
from pyfcm import FCMNotification
from django.conf import settings
from core import models as coremodels
from core import serializers as coreserializers
from library import models as librarymodels
from library import serializers as libraryserializers
from student import models as studentmodels
from student import serializers as studentserializers

from django.db.models import Q
from django.db.models import Avg, Count, Min, Sum
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.mail import EmailMessage
import json
import ast
from rest_framework.generics import *  
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError

from django.core.mail import EmailMultiAlternatives
from django.template import Context
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from django.core.files.storage import default_storage

class OwnerAPIViewSet(viewsets.ModelViewSet):
    queryset = models.Owner.objects.all()
    serializer_class = serializers.OwnerSerializer
    permission_classes = [permissions.IsAuthenticated, ]
    http_method_names = ['post','options','head']

    def get_queryset(self):
        queryset = models.Owner.objects.all()

        user = self.request.query_params.get('user', None)
        if user is not None:
            queryset = queryset.filter(user__id = user)

        branch = self.request.query_params.get('branch', None)
        if branch is not None:
            branch = get_object_or_404(librarymodels.LibraryBranch, id=id)
            queryset = queryset.filter(branches__in = [branch])

        queryset = queryset.order_by('name')

        search = self.request.query_params.get('search', None)
        if search is not None:
            queryset = queryset.filter(Q(name__icontains  =search)|Q(address__icontains  =search)|Q(city__icontains  =search)|Q(state__icontains  =search)|Q(location__icontains  =search))
        return queryset


    def create(self, request, *args, **kwargs):
        mobile = request.data.get('mobile')
        dob = request.data.get('dob')
        if 'user' not in request.data:    
            try:            
                user = coremodels.User.objects.create_user(username=mobile, password=dob,email=request.data['email'],is_owner=True)
            except IntegrityError:
                return Response("User already exisiting with same phone number please check",status=400)
            request.data['user'] = user.id
        if "branches" in request.data:
            if request.data['source'] == 'flutter':
                request.data['branches'] =  ast.literal_eval(request.data['branches'])
                request.data['branches'] = request.data['branches'][0]
            elif request.data['source'] == 'web':
                request.data['branches'] =  ast.literal_eval(request.data['branches'])

        if 'user' not in request.data:
            serializer = self.get_serializer(data=request.data)
            #serializer.is_valid(raise_exception=True)
            if not serializer.is_valid():
                user.delete()
                raise ValidationError(serializer.errors)
            else:
                self.perform_create(serializer)
        else:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
        owner = self.queryset.get(id=serializer.data["id"])
        sub = models.OwnerSubscriptionPlan.objects.create(owner = owner,title="Free Tier",days=45,branchesAllowed=2,amount=0,active=True)
        sub.save()
        owner.active_subscription = sub
        owner.save()
        # headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=200)

class OwnerAPIEdit(RetrieveUpdateAPIView):

    queryset = models.Owner.objects.all()
    serializer_class = serializers.OwnerSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def retrieve(self,request,*args,**kwargs):
        owner = self.queryset.get(user_id=self.kwargs['pk'])
        serializer = self.serializer_class(owner,context={'request': request})
        return Response(serializer.data)
    
    def partial_update(self,request,*args,**kwargs):
        owner = self.queryset.get(user_id=self.kwargs['pk'])
        if 'branches' in request.data:
            if request.data['source'] == 'flutter':
                request.data['branches'] =  ast.literal_eval(request.data['branches'])
                request.data['branches'] = request.data['branches'][0]
            elif request.data['source'] == 'web':
                request.data['branches'] =  ast.literal_eval(request.data['branches'])        
        serializer = self.serializer_class(owner,context={'request': request},data=request.data,partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=200)
class UserLibraryPermissionsAPIViewSet(viewsets.ModelViewSet):
    queryset = models.UserLibraryPermissions.objects.all()
    serializer_class = serializers.UserLibraryPermissionsSerializer
    permission_classes = [permissions.IsAuthenticated, ]


class EmployeeAPIViewSet(viewsets.ModelViewSet):
    queryset = models.Employee.objects.all()
    serializer_class = serializers.EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def get_queryset(self):
        queryset = models.Employee.objects.all()

        user = self.request.query_params.get('user', None)
        if user is not None:
            queryset = queryset.filter(user__id = user)

        branch = self.request.query_params.get('branch', None)
        if branch is not None:
            branch = get_object_or_404(librarymodels.LibraryBranch, id=id)
            queryset = queryset.filter(branches__in = [branch])

        search = self.request.query_params.get('search', None)
        if search is not None:
            queryset = queryset.filter(Q(name__icontains  =search)|Q(address__icontains  =search)|Q(city__icontains  =search)|Q(state__icontains  =search)|Q(location__icontains  =search))
        
        queryset = queryset.order_by('name')
        return queryset

    def create(self, request, *args, **kwargs):
        mobile = request.data.get('mobile')
        dob = request.data.get('dob')
        user = coremodels.User.objects.create_user(username=mobile, password=dob,email=request.data['email'],is_employee=True)
        request.data['user'] = user.id
        if request.data['source'] == 'flutter':
            request.data['branches'] =  ast.literal_eval(request.data['branches'])
            request.data['branches'] = request.data['branches'][0]
        elif request.data['source'] == 'web':
            request.data['branches'] =  ast.literal_eval(request.data['branches'])
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        # headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=200)



class EnquiryAPIViewSet(viewsets.ModelViewSet):
    queryset = models.Enquiry.objects.all()
    serializer_class = serializers.EnquirySerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def get_queryset(self):
        queryset = models.Enquiry.objects.all()

        branch = self.request.query_params.get('branch', None)
        if branch is not None:
            queryset = queryset.filter(library_branch__id=branch)

        search = self.request.query_params.get('search', None)
        if search is not None:
            queryset = queryset.filter(Q(name_icontains = search) | Q(comment_icontains = search))

        from_date = self.request.query_params.get('from_Date', None)
        if from_date is not None:
            from_date = datetime.datetime.strptime(from_date, "%Y-%m-%d").date()
            queryset = queryset.filter(date__gte = from_date)

        to_date = self.request.query_params.get('to_date', None)
        if to_date is not None:
            to_date = datetime.datetime.strptime(to_date, "%Y-%m-%d").date()
            queryset = queryset.filter(date__lte = to_date)

        follow_up_today = self.request.query_params.get('follow_up_today', None)
        if follow_up_today is not None:
            queryset = queryset.filter(follow_up_date=datetime.date.today())

        status = self.request.query_params.get('status', None)
        if status is not None:
            queryset = queryset.filter(status=status)
        return queryset

class EnquiryFollowUpAPIViewSet(viewsets.ModelViewSet):
    queryset = models.EnquiryFollowUp.objects.all()
    serializer_class = serializers.EnquiryFollowUpSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def get_queryset(self):
        queryset = models.EnquiryFollowUp.objects.all()

        enquiry = self.request.query_params.get('enquiry', None)
        if enquiry is not None:
            queryset = queryset.filter(enquiry__id=enquiry)

        search = self.request.query_params.get('search', None)
        if search is not None:
            queryset = queryset.filter(Q(title_icontains = search) | Q(details_icontains = search))

        from_date = self.request.query_params.get('from_Date', None)
        if from_date is not None:
            from_date = datetime.datetime.strptime(from_date, "%Y-%m-%d").date()
            queryset = queryset.filter(date__gte = from_date)

        to_date = self.request.query_params.get('to_date', None)
        if to_date is not None:
            to_date = datetime.datetime.strptime(to_date, "%Y-%m-%d").date()
            queryset = queryset.filter(date__lte = to_date)

        follow_up_today = self.request.query_params.get('follow_up_today', None)
        if follow_up_today is not None:
            queryset = queryset.filter(next_follow_up_date=datetime.date.today())

        return queryset


class ExpenseAPIViewSet(viewsets.ModelViewSet):
    queryset = models.Expense.objects.all()
    serializer_class = serializers.ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def get_queryset(self):
        queryset = models.Expense.objects.all()

        branch = self.request.query_params.get('branch', None)
        if branch is not None:
            queryset = queryset.filter(library_branch__id = branch)

        from_date = self.request.query_params.get('from_Date', None)
        if from_date is not None:
            from_date = datetime.datetime.strptime(from_date, "%Y-%m-%d").date()
            queryset = queryset.filter(date__gte = from_date)

        to_date = self.request.query_params.get('to_date', None)
        if to_date is not None:
            to_date = datetime.datetime.strptime(to_date, "%Y-%m-%d").date()
            queryset = queryset.filter(date__lte = to_date)

        year = self.request.query_params.get('year', None)
        if year is not None:
            queryset = queryset.filter(date__year = year)

        month = self.request.query_params.get('month', None)
        if month is not None:
            queryset = queryset.filter(date__month = month)

        search = self.request.query_params.get('search', None)
        if search is not None:
            queryset = queryset.filter(Q(title__icontains  =search)|Q(note__icontains  =search))

        queryset = queryset.order_by('-date')
        return queryset

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def monthly_expenses(self, request, *args, **kwargs):
        serializer_context = {
                'request': request,
        }
        result = {}
        queryset = self.get_queryset()

        from_date = self.request.query_params.get('from_Date', None)
        if from_date is not None:
            from_date = datetime.datetime.strptime(from_date, "%Y-%m-%d").date()
            queryset = queryset.filter(date__gte = from_date)

        to_date = self.request.query_params.get('to_date', None)
        if to_date is not None:
            to_date = datetime.datetime.strptime(to_date, "%Y-%m-%d").date()
            queryset = queryset.filter(date__lte = to_date)

        search = self.request.query_params.get('search', None)
        if search is not None:
            queryset = queryset.filter(title__icontains  =search)

        for current_month in range(1, 13):
            qs = queryset.filter(date__month=current_month).annotate(total=Sum("amount_paid"))
            result[current_month] = serializers.ExpenseSerializer(qs, many=True, context=serializer_context).data
        return Response(result)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def monthly_expenses2(self, request, *args, **kwargs):
        serializer_context = {
                'request': request,
        }
        result = []
        queryset = self.get_queryset()
        print(queryset)
        for current_month in range(1, 13):
            month_data = {
                "month": current_month,
            }
            qs = queryset.filter(date__month=current_month).annotate(total=Sum("amount_paid"))
            month_data["expenses"] = serializers.ExpenseSerializer(qs, many=True, context=serializer_context).data
            result.append(month_data)
        return Response(result)


class FeedbackAPIViewSet(viewsets.ModelViewSet):
    queryset = models.Feedback.objects.all()
    serializer_class = serializers.FeedbackSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def get_queryset(self):
        queryset = models.Feedback.objects.all()

        branch = self.request.query_params.get('branch', None)
        if branch is not None:
            queryset = queryset.filter(library_branch__id = branch)

        student = self.request.query_params.get('student', None)
        if student is not None:
            queryset = queryset.filter(student__id = student)

        from_date = self.request.query_params.get('from_Date', None)
        if from_date is not None:
            from_date = datetime.datetime.strptime(from_date, "%Y-%m-%d").date()
            queryset = queryset.filter(date__gte = from_date)

        to_date = self.request.query_params.get('to_date', None)
        if to_date is not None:
            to_date = datetime.datetime.strptime(to_date, "%Y-%m-%d").date()
            queryset = queryset.filter(date__lte = to_date)

        date = self.request.query_params.get('date', None)
        if date is not None:
            date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
            queryset = queryset.filter(date = date)

        year = self.request.query_params.get('year', None)
        if year is not None:
            queryset = queryset.filter(date__year = year)

        month = self.request.query_params.get('month', None)
        if month is not None:
            queryset = queryset.filter(date__month = month)

        search = self.request.query_params.get('search', None)
        if search is not None:
            queryset = queryset.filter(Q(title__icontains  =search)|Q(details__icontains  =search))

        active = self.request.query_params.get("active")
        if active is not None:
            queryset = queryset.filter(active = True)

        type = self.request.query_params.get("type")
        if type is not None:
            queryset = queryset.filter(type=type)

        queryset = queryset.order_by('date')
        return queryset

    def create(self,request,*args,**kwargs):
        
        if request.data["type"]=="Complaint":
            
            title = "Thank For Complaining. Your Complaint has been successfully registered"
            description = "Thank For Complaining. Your Complaint has been successfully registered \n We have started looking into the details. We will update your once the issue is ressolved.\n\nThank you"
            notiftype = "Complaint Registered"

            notif = coremodels.Notifications.objects.create(student=student,title=title,description=description,notifType=notiftype)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
class FeedbackFollowUpAPIViewSet(viewsets.ModelViewSet):
    queryset = models.FeedbackFollowUp.objects.all()
    serializer_class = serializers.FeedbackFollowUpSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def get_queryset(self):
        queryset = models.FeedbackFollowUp.objects.all()

        feedback = self.request.query_params.get('feedback', None)
        if feedback is not None:
            queryset = queryset.filter(feedback__id=feedback)

        search = self.request.query_params.get('search', None)
        if search is not None:
            queryset = queryset.filter(Q(title_icontains = search) | Q(detail_icontains = search))

        from_date = self.request.query_params.get('from_Date', None)
        if from_date is not None:
            from_date = datetime.datetime.strptime(from_date, "%Y-%m-%d").date()
            queryset = queryset.filter(date__gte = from_date)

        to_date = self.request.query_params.get('to_date', None)
        if to_date is not None:
            to_date = datetime.datetime.strptime(to_date, "%Y-%m-%d").date()
            queryset = queryset.filter(date__lte = to_date)

        return queryset
class EmployeeFeedbackAPIViewSet(viewsets.ModelViewSet):
    queryset = models.EmployeeFeedback.objects.all()
    serializer_class = serializers.EmployeeFeedbackSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def get_queryset(self):
        queryset = self.queryset

        branch = self.request.query_params.get('branch', None)
        if branch is not None:
            queryset = queryset.filter(library_branch__id = branch)

        student = self.request.query_params.get('student', None)
        if student is not None:
            queryset = queryset.filter(student__id = student)

        from_date = self.request.query_params.get('from_Date', None)
        if from_date is not None:
            from_date = datetime.datetime.strptime(from_date, "%Y-%m-%d").date()
            queryset = queryset.filter(date__gte = from_date)

        to_date = self.request.query_params.get('to_date', None)
        if to_date is not None:
            to_date = datetime.datetime.strptime(to_date, "%Y-%m-%d").date()
            queryset = queryset.filter(date__lte = to_date)

        year = self.request.query_params.get('year', None)
        if year is not None:
            queryset = queryset.filter(date__year = year)

        month = self.request.query_params.get('month', None)
        if month is not None:
            queryset = queryset.filter(date__month = month)

        search = self.request.query_params.get('search', None)
        if search is not None:
            queryset = queryset.filter(Q(title__icontains  =search)|Q(details__icontains  =search))

        active = self.request.query_params.get("active")
        if active is not None:
            queryset = queryset.filter(active = True)

        type = self.request.query_params.get("type")
        if type is not None:
            queryset = queryset.filter(type=type)

        queryset = queryset.order_by('date')
        return queryset

class EmployeeFeedbackFollowUpAPIViewSet(viewsets.ModelViewSet):
    queryset = models.EmployeeFeedbackFollowUp.objects.all()
    serializer_class = serializers.EmployeeFeedbackFollowUpSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def get_queryset(self):
        queryset = self.queryset

        feedback = self.request.query_params.get('feedback', None)
        if feedback is not None:
            queryset = queryset.filter(feedback__id=feedback)

        search = self.request.query_params.get('search', None)
        if search is not None:
            queryset = queryset.filter(Q(title_icontains = search) | Q(detail_icontains = search))

        from_date = self.request.query_params.get('from_Date', None)
        if from_date is not None:
            from_date = datetime.datetime.strptime(from_date, "%Y-%m-%d").date()
            queryset = queryset.filter(date__gte = from_date)

        to_date = self.request.query_params.get('to_date', None)
        if to_date is not None:
            to_date = datetime.datetime.strptime(to_date, "%Y-%m-%d").date()
            queryset = queryset.filter(date__lte = to_date)

        return queryset
class InvoiceEmailAPI(APIView):
    permission_classes = [permissions.IsAuthenticated, ]

    def post(self,request):
        instance = studentmodels.StudentPayment.objects.get(id=request.data["id"])
        mail=instance.purchased_subscription.student.email

        if not instance.invoice:
            return Response("No Invoice found please check",status=400)
   
        html_content = render_to_string('ownerinvoice.html', {'date': instance.date,'payment_mode':instance.payment_mode})
        text_content = strip_tags(html_content)
        email = EmailMultiAlternatives('Payment Invoice', text_content,'testingserver.12307@gmail.com',[mail,])
        email.attach_alternative(html_content, "text/html")

        docfile = default_storage.open(instance.invoice.name, 'r')
        email.attach(docfile.name, docfile.read())

        email.send()
        return Response("email sent successfully",status=200)

class OwnerInvoiceEmailAPI(APIView):                          #add restrictions
    permission_classes = [permissions.IsAuthenticated, ]

    def post(self,request):
        instance = models.Expense.objects.get(id=request.data["id"])
        try:
            onwer = models.Owner.objects.get(user=request.user)
        except ObjectDoesNotExist:
            return Response({"error":"User is Not an Owner"},status=400)
        mail=onwer.email

        if not instance.invoice:
            return Response("No Invoice found please check",status=400)
   
        html_content = render_to_string('ownerexpenseinvoice.html', {'date': instance.date,'payment_mode':instance.payment_mode,'amount':instance.amount_paid})
        text_content = strip_tags(html_content)
        email = EmailMultiAlternatives('Expense Invoice', text_content,'testingserver.12307@gmail.com',[mail,])
        email.attach_alternative(html_content, "text/html")

        docfile = default_storage.open(instance.invoice.name, 'r')
        email.attach(docfile.name, docfile.read())

        email.send()
        return Response("email sent successfully",status=200)

# class BranchOwnerListAPI(ListAPIView):

#     queryset = models.Owner.objects.all()
#     serializer_class = serializers.OwnerSerializer
#     permission_classes = [permissions.IsAuthenticated, ] 

#     def get_queryset(self):
#         queryset = self.queryset.filter(branches=self.kwargs["id"])
#         search = self.request.query_params.get('search', None)
#         if search is not None:
#             queryset = queryset.filter(name__icontains  = search)
#         return queryset   

class BranchEmployeeListAPI(ListAPIView,CreateAPIView):

    queryset = models.Employee.objects.all()
    serializer_class = serializers.EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def get_queryset(self):
        queryset = self.queryset.filter(branches=self.kwargs["id"])
        search = self.request.query_params.get('search', None)
        if search is not None:
            queryset = queryset.filter(name__icontains  = search)
        return queryset

    def list(self,request,*args,**kwargs):

        if not request.user.is_owner:
            return Response({"error":"User is not an owner"},status=401)

        instance = models.Owner.objects.get(user = request.user)
       
        branchlist = instance.branches.all()
        if int(kwargs["id"]) not in branchlist.values_list('id', flat=True):
            return Response({"Error":"Branch does not belong to this owner"},status=403)

        queryset = self.get_queryset()

        serializer  = self.serializer_class(queryset,many=True)

        return Response(serializer.data, status= 200)

    def create(self, request, *args, **kwargs):
        if not request.user.is_owner:
            return Response({"error":"User is not an owner"},status=401)
                
        instance = models.Owner.objects.get(user = request.user)

        mobile = request.data.get('mobile')
        dob = request.data.get('dob')
        user = coremodels.User.objects.create_user(username=mobile, password=dob,email=request.data['email'],is_employee=True)
        request.data['user'] = user.id
        if 'source' in request.data:
            if request.data['source'] == 'flutter':
                request.data['branches'] =  ast.literal_eval(request.data['branches'])
                request.data['branches'] = request.data['branches'][0]
            elif request.data['source'] == 'web':
                request.data['branches'] =  ast.literal_eval(request.data['branches'])

        for branch in request.data["branches"]:
            branchlist = instance.branches.all()
            if branch not in branchlist.values_list('id', flat=True):
                user.delete()
                return Response({"Error":"Branch does not belong to this owner/employee"},status=403)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        # headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=200)             

class BranchEmployeeUpdateAPI(RetrieveAPIView,UpdateAPIView):

    queryset = models.Employee.objects.all()
    serializer_class = serializers.EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def retrieve(self,request,*args,**kwargs):

        instance = self.queryset.get(id=kwargs["pk"])

        serializer = self.get_serializer(instance)

        return Response(serializer.data,status=200)
    
    def partial_update(self,request,*args,**kwargs):

        instance = self.queryset.get(id=kwargs["pk"])

        if not request.user.is_owner:
            return Response({"error":"User is not an owner"},status=401)

        owner = models.Owner.objects.get(user = request.user)

        if 'branches' in request.data:
            for branch in request.data["branches"]:
                branchlist = owner.branches.all()
                if branch not in branchlist.values_list('id', flat=True):
                    return Response({"Error":"Branch does not belong to this owner/employee"},status=403)
        
        serializer = self.get_serializer(instance,data=request.data,partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=200)


class OwnerDetailAPI(RetrieveAPIView):

    queryset = models.Owner.objects.all()
    serializer_class = serializers.OwnerSerializer
    permission_classes = [permissions.IsAuthenticated, ] 

    def retrieve(self,request,*args,**kwargs):
        try:
            owner = self.queryset.get(user=self.kwargs["id"])
        except ObjectDoesNotExist:
            return Response(" Not an Owner or wrong user",status=400)
        serializer = self.serializer_class(owner,context={'request': request})
        #return Response(request.headers['Origin'],status=200)
        return Response(serializer.data,status=200)

            
class DueDateNotificationAPI(APIView):

    def post(self,request,id):
        try:
            student = studentmodels.Student.objects.get(id=id)
        except ObjectDoesNotExist:
            return Response("Invalid Student ID",status=400)
        
        title = "Subscription due date coming in : "+str(request.data["due_days"])+'\n Please Renew the subscription'
        description = "Subscription getting due in " +str(request.data["due_days"])+"\n Please Renew the subscription to continue enjoying the library service."
        notiftype = "Subscription Due Date"

        notif = coremodels.Notifications.objects.create(student=student,title=title,description=description,notifType=notiftype)

        return Response("Notification Sent to the Student Successfully",status=200)

# class OwnerGraphIncomeExpenseAPI(APIView):
        
#     def get(self,request,id):
#         today = datetime.date.today()
#         qs1 = studentmodels.StudentPayment.objects.filter(purchased_subscription__student__library_branch=self.kwargs["id"])
#         qs2 = models.Expense.objects.filter(library_branch=self.kwargs["id"])
#         currentMonthIncome = qs1.filter(date__month=today.month,date__year=today.year)
#         currentMonthExpense = qs2.filter(date__month=today.month,date__year=today.year)
#         if today.month==1:
#             lastMonthIncome = qs1.filter(date__month=12,date__year=today.year-1)
#             lastMonthExpense = qs2.filter(date__month=12,date__year=today.year-1)
#         else:
#             lastMonthIncome = qs1.filter(date__month=today.month-1,date__year=today.year)
#             lastMonthExpense = qs2.filter(date__month=today.month-1,date__year=today.year)

#         CurrentIncome=0
#         LastIncome = 0
#         CurrentExpense=0
#         LastExpense = 0

#         for i in currentMonthIncome:
#             CurrentIncome = CurrentIncome +int (i.amount_paid) 
#         for i in lastMonthIncome:
#             LastIncome = LastIncome +int (i.amount_paid)
#         for i in currentMonthExpense:
#             CurrentExpense = CurrentExpense +int (i.amount_paid)
#         for i in lastMonthExpense:
#             LastExpense = LastExpense +int (i.amount_paid)

#         library_branch = librarymodels.LibraryBranch.objects.get(id=self.kwargs["id"])

#         data ={
#             "libraryName":library_branch.name,
#             "currentIncome":CurrentIncome,
#             "lastIncome":LastIncome,
#             "currentExpense":CurrentExpense,
#             "lastExpense":LastExpense
#         }

#         return Response(data,status=200)

# class FeedbackListAPI(ListAPIView,CreateAPIView):
#     queryset = models.Feedback.objects.all()
#     serializer_class = serializers.FeedbackMinSerializer
#     permission_classes = [permissions.IsAuthenticated, ]

#     def get_queryset(self):
#         queryset = self.queryset.filter(library_branch=self.kwargs["id"])

#         from_date = self.request.query_params.get('from_Date', None)
#         if from_date is not None:
#             from_date = datetime.datetime.strptime(from_date, "%Y-%m-%d").date()
#             queryset = queryset.filter(date__gte = from_date)

#         to_date = self.request.query_params.get('to_date', None)
#         if to_date is not None:
#             to_date = datetime.datetime.strptime(to_date, "%Y-%m-%d").date()
#             queryset = queryset.filter(date__lte = to_date)

#         search = self.request.query_params.get('search', None)
#         if search is not None:
#             queryset = queryset.filter(Q(title__icontains  =search)|Q(details__icontains  =search))

#         active = self.request.query_params.get("active")
#         if active is not None:
#             queryset = queryset.filter(active = True)

#         type = self.request.query_params.get("type")
#         if type is not None:
#             queryset = queryset.filter(type=type)

#         queryset = queryset.order_by('date')
#         return queryset

#     def create(self,request,*args,**kwargs):
        
#         if request.data["type"]=="Complaint":
            
#             title = "Thank For Complaining. Your Complaint has been successfully registered"
#             description = "Thank For Complaining. Your Complaint has been successfully registered \n We have started looking into the details. We will update your once the issue is ressolved.\n\nThank you"
#             notiftype = "Complaint Registered"

#             notif = coremodels.Notifications.objects.create(student=student,title=title,description=description,notifType=notiftype)

#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         self.perform_create(serializer)
#         headers = self.get_success_headers(serializer.data)
#         return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class OwnerEmployeeDashboardAPI(APIView):
    queryset = studentmodels.Student.objects.all()
    permission_classes = [permissions.IsAuthenticated, ]

    def get(self,request,id):
        if not request.user.is_owner and not request.user.is_employee:
            return Response({"error":"User is not an owner/employee"},status=401)
        
        if request.user.is_owner:
            instance = models.Owner.objects.get(user = request.user)
        elif request.user.is_employee:
            instance = models.Employee.objects.get(user = request.user)
        
        branchlist = instance.branches.all()
        if int(id) not in branchlist.values_list('id', flat=True):
            return Response({"Error":"Branch does not belong to this owner/employee"},status=403)   

        time = datetime.datetime.now()
        today = datetime.date.today()
        branch = librarymodels.LibraryBranch.objects.get(id=id)

        students = self.queryset.filter(library_branch=id)
        bookedHours=0
        d0 = datetime.datetime(year=today.year, month=today.month+1, day=1)
        d1 = datetime.datetime(year=today.year, month=today.month, day=1)
        days = (d0-d1).days

        for student in students:
            if student.active_subscription is None:
                pass
            else:
                bookedHours = bookedHours + (student.active_subscription.shift_timings*student.active_subscription.days)
        if branch.opening_time.hour == branch.closing_time.hour:
            availablehours = 24 * (branch.opening_days.all()).count()*days - bookedHours
        else:           
            availablehours = int(branch.closing_time.hour-branch.opening_time.hour)*days * (branch.opening_days.all()).count() - bookedHours
        
        present = studentmodels.StudentAttendance.objects.filter(branch=id,slot__start__lte=time,slot__end__gte=time,date=today,present=True)
        offtime = studentmodels.StudentAttendance.objects.filter(Q(branch=id,slot__start__gte=time,date=today)|Q(branch=id,slot__end__lte=time,out_time__isnull=True,date=today))
        nottimeSlots = coremodels.TimeSlot.objects.filter(~Q(start__lte=time,end__gte=time))
        currentSlots = coremodels.TimeSlot.objects.filter(start__lte=time,end__gte=time)
        
        renewals=0
        admission=0
        pending = 0

        for student in students:
            if student.active_subscription is None:
                pass
            else:
                payments = studentmodels.StudentPayment.objects.filter(purchased_subscription=student.active_subscription).aggregate(Sum('amount_paid'))
                payments = payments['amount_paid__sum']
                if payments:
                    if student.active_subscription.total_amount - payments>0:
                        pending = pending + 1 
                sub = studentmodels.PurchasedSubscription.objects.filter(student=student)

                if sub.count()==1:
                    admission = admission+1
                elif sub.count()>1:
                    renewals=renewals+1
            
        lockers = librarymodels.LibraryLocker.objects.filter(library_branch=id,assigned_student__isnull=True,active=True)
        totallockers = librarymodels.LibraryLocker.objects.filter(library_branch=id,active=True)
        data={
            "maxHours":int(branch.closing_time.hour-branch.opening_time.hour)*days * (branch.opening_days.all()).count(),
            "bookHours":bookedHours,
            "availableHours":availablehours,
            "total seats":branch.seat_capacity,
            "present":present.count()+offtime.count(),
            "offtime":offtime.count(),
            "total locker":totallockers.count(),
            "open locker":lockers.count(),
            "pendings":pending,
            "renewal":renewals,
            "admission":admission
        }

        return Response(data,status=200)

class OTPEmailAPI(APIView):
    permission_classes = [permissions.IsAuthenticated, ]

    def post(self,request):

        html_content = render_to_string('otp/otp.html', {'otp': request.data["otp"]})
        text_content = strip_tags(html_content)
        email = EmailMultiAlternatives('SRMS Verification OTP', text_content,'testingserver.12307@gmail.com',[request.data["mail"],])
        email.attach_alternative(html_content, "text/html")
        #msg = 'Dear Student,\n\nThe Verification OTP is \n\n'+str(request.data["otp"])+'\n\n If there are any issues, Please contatc SRMS admin.\nThank you  \n\nRegards,\nTeam SRMS'
        #email = EmailMessage(subject='SRMS Verification OTP',body=msg,from_email='testingserver.12307@gmail.com',to=[request.data["mail"],])

        email.send()
        return Response("email sent successfully",status=200)

class ActiveBranchAPI(APIView):

    def get(self,request):
        try:
            owner = models.Owner.objects.get(user=request.user)
        except ObjectDoesNotExist:
            return Response({"error":"User is Not an Owner"},status=400)
        try:
            ownersub = models.OwnerSubscriptionPlan.objects.get(id=owner.active_subscription.id)
        except ObjectDoesNotExist:
            return Response("No active Subscription",status=400)
        data=[]
        if owner.branches.all().count() == ownersub.activeBranch.all().count():
            data.append(
                {
                    "id":"all",
                    "name":"All"
                }
            )
        
        for branch in ownersub.activeBranch.all():
            data.append(
                {
                    "id":branch.id,
                    "name":branch.name
                }
            )        

        return Response(data,status=200)   

class PartnerAPI(ListAPIView,CreateAPIView):

    queryset = models.Owner.objects.all()
    serializer_class = serializers.OwnerSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def list(self,request,*args,**kwargs):

        if not request.user.is_owner:
            return Response({"error":"User is not an owner/employee"},status=401)
                
        instance = models.Owner.objects.get(user = request.user)
        
        branchlist = instance.branches.all()
        if int(kwargs["id"]) not in branchlist.values_list('id', flat=True):
            return Response({"Error":"Branch does not belong to this owner/employee"},status=403) 

        queryset =self.queryset.filter(branches__in=[kwargs["id"]])
        
        data=[]
        for i in queryset:
            serializer = serializers.OwnerMinSerializer(i)
            data.append({
                "details":serializer.data,
                "owner":i.user.is_owner,
                "employee":i.user.is_employee,

            })
        
        return Response(data,status=200)

    def create(self,request,*args,**kwargs):
        if not request.user.is_owner:
            return Response({"error":"User is not an owner"},status=401)
                
        instance = models.Owner.objects.get(user = request.user)
        
        branchlist = instance.branches.all()
        if int(kwargs["id"]) not in branchlist.values_list('id', flat=True):
            return Response({"Error":"Branch does not belong to this owner/employee"},status=403) 

        mobile = request.data.get('mobile')
        dob = request.data.get('dob')
        if 'user' not in request.data:                
            try:            
                user = coremodels.User.objects.create_user(username=mobile, password=dob,email=request.data['email'],is_owner=True)
            except IntegrityError:
                return Response("User already exisiting with same phone number please check",status=400)
            request.data['user'] = user.id

        if "source" in request.data:
            if request.data['source'] == 'flutter':
                request.data['branches'] = ast.literal_eval(request.data['branches'])
                request.data['branches'] = request.data['branches'][0]

        for branch in request.data["branches"]:
            branchlist = instance.branches.all()
            if branch not in branchlist.values_list('id', flat=True):
                user.delete()
                return Response({"Error":"Branch does not belong to this owner/employee"},status=403)

        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            user.delete()
            raise ValidationError(serializer.errors)
        else:
            self.perform_create(serializer)

        owner = self.queryset.get(id=serializer.data["id"])
        sub = models.OwnerSubscriptionPlan.objects.create(owner = owner,title="Free Tier",days=45,branchesAllowed=2,amount=0,active=True)
        if owner.branches.all().count()<=2:
            for branch in owner.branches.all():
                sub.activeBranch.add(branch.id)
        else:
            for branch in request.data["activebranches"]:
                sub.activeBranch.add(branch)
        sub.save()
        owner.active_subscription = sub
        owner.save()
        # headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=200)

class BranchHolidayAPI(ListAPIView,CreateAPIView):

    queryset = librarymodels.Holidays.objects.all()
    serializers = libraryserializers.HolidaysSerializer
    permission_classes = [permissions.IsAuthenticated,]

    def list(self,request,*args,**kwargs):
        if not request.user.is_owner and not request.user.is_employee:
            return Response({"error":"User is not an owner/employee"},status=401)

        if request.user.is_owner:
            instance = models.Owner.objects.get(user = request.user)
        elif request.user.is_employee:
            instance = models.Employee.objects.get(user = request.user)

        branchlist = instance.branches.all()
        if int(kwargs["id"]) not in branchlist.values_list('id', flat=True):
            return Response({"Error":"Branch does not belong to this owner/employee"},status=403)

        queryset = self.queryset.filter(library_branch=kwargs["id"])

        serializer = self.serializer_class(queryset,many=True)

        return Response(serializer.data,status=200)        

    def create(self,request,*args,**kwargs):

        if not request.user.is_owner and not request.user.is_employee:
            return Response({"error":"User is not an owner/employee"},status=401)

        if request.user.is_owner:
            instance = models.Owner.objects.get(user = request.user)
        elif request.user.is_employee:
            instance = models.Employee.objects.get(user = request.user)

        branchlist = instance.branches.all()
        if int(kwargs["id"]) not in branchlist.values_list('id', flat=True):
            return Response({"Error":"Branch does not belong to this owner/employee"},status=403)

        students = studentmodels.Student.objects.filter(library_branch=request.data["library_branch"])
        for student in students:
            title = "New Holiday has been added on : "+str(request.data["start"])+str(request.data['title'])
            description = "Holiday has been added \n"+str(request.data["details"])
            notiftype = "holiday"

            notif = coremodels.Notifications.objects.create(student=student,title=title,description=description,notifType=notiftype)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class BranchHolidayUpdateAPI(RetrieveAPIView,UpdateAPIView,DestroyAPIView):
    queryset = librarymodels.Holidays.objects.all()
    serializers = libraryserializers.HolidaysSerializer
    permission_classes = [permissions.IsAuthenticated,]

    def retrieve(self, request, *args, **kwargs):
        if not request.user.is_owner and not request.user.is_employee:
            return Response({"error":"User is not an owner/employee"},status=401)

        if request.user.is_owner:
            instance = models.Owner.objects.get(user = request.user)
        elif request.user.is_employee:
            instance = models.Employee.objects.get(user = request.user)

        branchlist = instance.branches.all()
        if int(kwargs["id"]) not in branchlist.values_list('id', flat=True):
            return Response({"Error":"Branch does not belong to this owner/employee"},status=403)
        
        queryset = self.queryset.get(id=kwargs["pk"])

        serializer = self.get_serializer(queryset)

        return Response(serializer.data,status=200)

    def partial_update(self, request, *args, **kwargs):
        if not request.user.is_owner and not request.user.is_employee:
            return Response({"error":"User is not an owner/employee"},status=401)

        if request.user.is_owner:
            instance = models.Owner.objects.get(user = request.user)
        elif request.user.is_employee:
            instance = models.Employee.objects.get(user = request.user)

        branchlist = instance.branches.all()
        if int(kwargs["id"]) not in branchlist.values_list('id', flat=True):
            return Response({"Error":"Branch does not belong to this owner/employee"},status=403)
        
        queryset = self.queryset.get(id=kwargs["pk"])

        serializer = self.get_serializer(queryset,data=request.data,partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data,status=200)

    def delete(self,request,*args,**kwargs):

        if not request.user.is_owner and not request.user.is_employee:
            return Response({"error":"User is not an owner/employee"},status=401)

        if request.user.is_owner:
            instance = models.Owner.objects.get(user = request.user)
        elif request.user.is_employee:
            instance = models.Employee.objects.get(user = request.user)

        branchlist = instance.branches.all()
        if int(kwargs["id"]) not in branchlist.values_list('id', flat=True):
            return Response({"Error":"Branch does not belong to this owner/employee"},status=403)
        
        queryset = self.queryset.get(id=kwargs["pk"])

        queryset.delete()

        return Response("ok",status=200)

class OwnerDeviceRegAPI(CreateAPIView):

    queryset = models.OwnerDevice.objects.all()
    serializer_class = serializers.OwnerDeviceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self,request,*args,**kwargs):
        if not request.user.is_owner:
            return Response({"error":"Not an owner"},status=403)
        owner = models.Owner.objects.get(user=request.user)
        try:
            instance = self.queryset.get(owner=owner,registration_id=request.data["registration_id"])
        except ObjectDoesNotExist:

            request.data["owner"]=owner.id
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)

            push_service = FCMNotification(api_key=settings.FCM_APIKEY)

            registration_id = request.data["registration_id"]
            message_title = "testing update"
            message_body = "testing hello"
            result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title, message_body=message_body)

            return Response("Success",status=200)

        push_service = FCMNotification(api_key=settings.FCM_APIKEY)

        registration_id = request.data["registration_id"]
        owner.registration_id = request.data["registration_id"]
        owner.save()
        message_title = "testing update"
        message_body = "registered hello"
        result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title, message_body=message_body)
        print(result)

        return Response("Token re-registrated",status=200)

class OwnerPlanView(ListAPIView):

    queryset = models.OwnerSubPlan.objects.all()
    serializer_class = serializers.OwnerSubPlanSerializer
    permission_classes = [permissions.IsAuthenticated,]


class ManageInvoiceOwner(APIView):

    queryset = models.Expense.objects.all()

    permission_classes = [permissions.IsAuthenticated,]

    def get(self,request,id):

        today = datetime.date.today()

        if not request.user.is_owner:
            return Response({"error":"User is not an owner"},status=401)
                
        instance = models.Owner.objects.get(user = request.user)

        branchlist = instance.branches.all()
        if int(id) not in branchlist.values_list('id', flat=True):
            return Response({"Error":"Branch does not belong to this owner"},status=403) 

        queryset = self.queryset.filter(library_branch = id).order_by('date')
        monthwise = []
        startyear = (queryset.first()).date.year
        lastyear = (queryset.last()).date.year
        for i in reversed(range(startyear,lastyear+1)):
            if i == today.year:
                startmonth = 1
                endmonth = today.month
            else:
                startmonth = 1
                endmonth = 12
            for j in reversed(range(startmonth,endmonth+1)):
                data=[]
                expense = 0
                queryset = self.queryset.filter(library_branch=id)
                queryset = queryset.filter(library_branch=id,date__month=j,date__year=i)
                if queryset.count()==0:
                    continue
                for k in queryset:
                    if k.invoice:
                        invoice = k.invoice
                    else:
                        invoice = None
                    data.append(
                    {
                        "title":k.title,
                        "note":k.note,
                        "amount":k.amount_paid,
                        "invoice":invoice
                    })
                monthwise.append(
                    {
                        "year":i,
                        "month":j,
                        "data":data
                    }
                )
            
        return Response(monthwise,status=200)        

class ManageInvoiceStudent(APIView):

    queryset = studentmodels.Student.objects.all()

    permission_classes = [permissions.IsAuthenticated,]

    def get(self,request,id):

        today = datetime.date.today()

        if not request.user.is_owner:
            return Response({"error":"User is not an owner"},status=401)
                
        instance = models.Owner.objects.get(user = request.user)

        branchlist = instance.branches.all()
        if int(id) not in branchlist.values_list('id', flat=True):
            return Response({"Error":"Branch does not belong to this owner"},status=403) 

        queryset = self.queryset.filter(library_branch = id)
        sub = studentmodels.PurchasedSubscription.objects.none()

        for student in queryset:
            pursub = studentmodels.PurchasedSubscription.objects.filter(student=student).order_by('date')


            pursub = pursub.first()
            if pursub is not None:
                sub = studentmodels.PurchasedSubscription.objects.filter(id=pursub.id) | sub

        sub = sub.order_by('date')

        monthwise = []
        startyear = (sub.first()).date.year
        lastyear = (sub.last()).date.year
        for i in reversed(range(startyear,lastyear+1)):
            if i == today.year:
                startmonth = 1
                endmonth = today.month
            else:
                startmonth = 1
                endmonth = 12
            for j in reversed(range(startmonth,endmonth+1)):
                data=[]
                expense = 0
                instances = sub.filter(date__month=j,date__year=i)
                if instances.count()==0:
                    continue
                for k in instances:
                    payments = studentmodels.StudentPayment.objects.filter(purchased_subscription=k).order_by('date')

                    payment = payments.first()
                    amount=payment.amount_paid
                    if payment.invoice:
                        invoice = payment.invoice
                    else:
                        invoice = None
                    timeslots = k.timeslots.all()
                    serializer = coreserializers.TimeSlotSerializer(timeslots,many=True)
                    data.append(
                    {
                        "student_name":k.student.name,
                        "student_id":k.student.id,
                        "amount":amount,
                        "invoice":invoice,
                        "timeslot":serializer.data
                    })
                monthwise.append(
                    {
                        "year":i,
                        "month":j,
                        "data":data
                    }
                )
            
        return Response(monthwise,status=200)        



    
