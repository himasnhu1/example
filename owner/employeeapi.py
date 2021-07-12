from django.shortcuts import render, get_object_or_404
from . import models, serializers
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
import datetime
from core import models as coremodels
from library import models as librarymodels
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


class EmployeeEnquiryApi(ListAPIView,CreateAPIView):

    queryset = models.Enquiry.objects.all()
    serializer_class = serializers.EnquirySerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def get_queryset(self):
        
        queryset = self.queryset.filter(library_branch=self.kwargs["id"])
        active = self.request.query_params.get('status', None)
        if status is not None:
            if status=="open":
                queryset = queryset.filter(status="Open")
            elif status=="closed":
                queryset = queryset.filter(Q(status="Registered")|Q(status="Withdrawed"))

        from_date = self.request.query_params.get('from_Date', None)

        if from_date is not None:
            from_date = datetime.datetime.strptime(from_date, "%Y-%m-%d").date()
            queryset = queryset.filter(add_date__gte = from_date)

        to_date = self.request.query_params.get('to_date', None)
        if to_date is not None:
            to_date = datetime.datetime.strptime(to_date, "%Y-%m-%d").date()
            queryset = queryset.filter(add_date__lte = to_date)
        
        search = self.request.query_params.get('search', None)
        if search is not None:
            queryset = queryset.filter(name__icontains  =search)

        return queryset

    def create(self,request,*args,**kwargs):

        if not request.user.is_owner and not request.user.is_employee:
            return Response({"Error":"Access Denied"},status=401)

        if request.user.is_owner:
            instance = models.Owner.objects.get(user=request.user)
        else:
            instance = models.Employee.objects.get(user=request.user)
        
        branchlist = instance.branches.all()
        if self.kwargs["id"] not in branchlist.values_list('id', flat=True):
        # if kwargs["id"] in instance.branches:
            return Response({"error":"Branch does not belong to the owner/employee"},status=403)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def list(self,request,*args,**kwargs):

        if not request.user.is_owner and not request.user.is_employee:
            return Response({"Error":"Access Denied"},status=401)

        if request.user.is_owner:
            instance = models.Owner.objects.get(user=request.user)
        else:
            instance = models.Employee.objects.get(user=request.user)
        
        branchlist = instance.branches.all()
        if self.kwargs["id"] not in branchlist.values_list('id', flat=True):
        # if kwargs["id"] in instance.branches:
            return Response({"error":"Branch does not belong to the owner/employee"},status=403)
        
        queryset = self.get_queryset()

        serializer = self.get_serializer(queryset,many=True)

        return Response(serializer.data,status=200)

class EmployeeEnquiryUpdateApi(UpdateAPIView):

    queryset = models.Enquiry.objects.all()
    serializer_class = serializers.EnquirySerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def partial_update(self,request,*args,**kwargs):

        if not request.user.is_owner and not request.user.is_employee:
            return Response({"Error":"Access Denied"},status=401)

        if request.user.is_owner:
            instance = models.Owner.objects.get(user=request.user)
        else:
            instance = models.Employee.objects.get(user=request.user)
        
        branchlist = instance.branches.all()
        if self.kwargs["id"] not in branchlist.values_list('id', flat=True):
        # if kwargs["id"] in instance.branches:
            return Response({"error":"Branch does not belong to the owner/employee"},status=403)

        enquiry = self.queryset.get(id=kwargs["pk"])
        serializer = self.serializer_class(enquiry,data=request.data,partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,status=200)

class EmployeeEnquiryFollowApi(CreateAPIView):

    queryset = models.EnquiryFollowUp.objects.all()
    serializer_class = serializers.EnquiryFollowUpSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def create(self,request,*args,**kwargs):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        enquiry = Enquiry.objects.get(id=request.data["enquiry"])
        data ={
            "follow_up_date": request.data["next_follow_up_date"]
        }
        serializer2 = EnquirySerializer(enquiry,data=data,partial=True)
        serializer2.is_valid(raise_exception=True)
        #enquiry.follow_up_date = datetime.datetime.strptime(request.data["next_follow_up_date"], "%Y-%m-%d").date()
        serializer2.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class EmployeeFeedbackListAPI(ListAPIView,CreateAPIView):
    queryset = models.Feedback.objects.all()
    serializer_class = serializers.FeedbackMinSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def list(self,request,*args,**kwargs):

        if not request.user.is_owner and not request.user.is_employee:
            return Response({"Error":"Access Denied"},status=401)

        if request.user.is_owner:
            instance = models.Owner.objects.get(user=request.user)
        else:
            instance = models.Employee.objects.get(user=request.user)
        
        branchlist = instance.branches.all()
        if kwargs["id"] not in branchlist.values_list('id', flat=True):
        # if kwargs["id"] in instance.branches:
            return Response({"error":"Branch does not belong to the owner/employee"},status=403)
        
        queryset = self.queryset.filter(library_branch=self.kwargs["id"])

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
            queryset = queryset.filter(Q(title__icontains  =search)|Q(details__icontains  =search))

        active = self.request.query_params.get("active")
        if active is not None:
            queryset = queryset.filter(active = True)

        type = self.request.query_params.get("type")
        if type is not None:
            queryset = queryset.filter(type=type)

        queryset = queryset.order_by('date')
        serializer = self.serializer_class(queryset,many=True)

        return Response(serializer.data,status=200) 

    def create(self,request,*args,**kwargs):
        if not request.user.is_owner and not request.user.is_employee:
            return Response({"Error":"Access Denied"},status=401)

        if request.user.is_owner:
            instance = models.Owner.objects.get(user=request.user)
        else:
            instance = models.Employee.objects.get(user=request.user)
        
        branchlist = instance.branches.all()
        if kwargs["id"] not in branchlist.values_list('id', flat=True):
        # if kwargs["id"] in instance.branches:
            return Response({"error":"Branch does not belong to the owner/employee"},status=403)

        student = studentmodels.Student.objects.get(id=request.data["student"]) 

        if request.data["type"]=="Complaint":
            
            title = "Thank For Complaining. Your Complaint has been successfully registered"
            description = "Thank For Complaining. Your Complaint has been successfully registered \n We have started looking into the details. We will update your once the issue is ressolved.\n\nThank you"
            notiftype = "Complaint Registered"

            notif = coremodels.Notifications.objects.create(student=student,title=title,description=description,notifType=notiftype)

        request.data["library_branch"]=kwargs["id"]
        print(request.data)
        serializer = serializers.FeedbackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class EmployeeFeedbackUpdateAPI(UpdateAPIView):
    queryset = models.Feedback.objects.all()
    serializer_class = serializers.FeedbackSerializer
    permission_classes = [permissions.IsAuthenticated, ]  

    def partial_update(self,request,*args,**kwargs):

        if not request.user.is_owner and not request.user.is_employee:
            return Response({"Error":"Access Denied"},status=401)

        if request.user.is_owner:
            instance = models.Owner.objects.get(user=request.user)
        else:
            instance = models.Employee.objects.get(user=request.user)
        
        branchlist = instance.branches.all()
        if kwargs["id"] not in branchlist.values_list('id', flat=True):
        # if kwargs["id"] in instance.branches:
            return Response({"error":"Branch does not belong to the owner/employee"},status=403)

        feedback = self.queryset.get(id=kwargs["pk"])

        if feedback.type == 'Complaint':
            title = "Your complaint registered on "+str(feedback.date)+" is ressolved"
            description = request.data["response"]
            notiftype = "Complaint Closed"

            notif = coremodels.Notifications.objects.create(student=feedback.student,title=title,description=description,notifType=notiftype)

        request.data["active"]= False
        serializer = self.serializer_class(feedback,data=request.data,partial=True)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        # headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=200)



class EmployeeExpenseAPI(APIView):
    queryset = models.Expense.objects.all()
    serializer_class = serializers.ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def get(self,request,id):

        if not request.user.is_owner and not request.user.is_employee:
            return Response({"Error":"Access Denied"},status=401)

        if request.user.is_owner:
            instance = models.Owner.objects.get(user=request.user)
        else:
            instance = models.Employee.objects.get(user=request.user)
        
        branchlist = instance.branches.all()
        if self.kwargs["id"] not in branchlist.values_list('id', flat=True):
        # if kwargs["id"] in instance.branches:
            return Response({"error":"Branch does not belong to the owner/employee"},status=403)

        today = datetime.datetime.today()
        data = []
        yearwise=[]
        queryset = self.queryset.filter(library_branch=id)

        from_date = self.request.query_params.get('from_date', None)
        if from_date is not None:
            from_date = datetime.datetime.strptime(from_date, "%Y-%m-%d").date()
            queryset = queryset.filter(date__gte = from_date)
        to_date = self.request.query_params.get('to_date', None)
        if to_date is not None:
            to_date = datetime.datetime.strptime(to_date, "%Y-%m-%d").date()
            queryset = queryset.filter(date__lte = to_date)

        if from_date is None and to_date is None:
            queryset = queryset.order_by('date')
            startyear = (queryset.first()).date.year
            lastyear = (queryset.last()).date.year
            for i in range(startyear,lastyear+1):
                data=[]
                if i == today.year:
                    startmonth = 1
                    endmonth = today.month
                else:
                    startmonth = 1
                    endmonth = 12
                for j in range(startmonth,endmonth+1):
                    expense = 0
                    queryset = self.queryset.filter(library_branch=id)
                    queryset = queryset.filter(library_branch=id,date__month=j,date__year=i)
                    for k in queryset:
                        
                        expense = expense + k.amount_paid
                    
                    data.append(
                        {
                            "month":j,
                            "expense":expense
                        }
                    )
                yearwise.append(
                    {
                        "year":i,
                        "details":data
                    }
                )
            return Response(yearwise,status=200)

        queryset = queryset.order_by('date')

        if queryset.count()==0:
            return Response(yearwise,status=200)
        startyear = (queryset.first()).date.year
        lastyear = (queryset.last()).date.year
        for i in range(startyear,lastyear+1):
            data=[]
            if i == today.year:
                startmonth = 1
                endmonth = today.month
            else:
                startmonth = 1
                endmonth = 12
            for j in range(startmonth,endmonth+1):
                expense = 0
                queryset = self.queryset.filter(library_branch=id,date__gte = from_date)
                queryset = queryset.filter(date__lte = to_date)
                queryset = queryset.filter(library_branch=id,date__month=j,date__year=i)

                for x in queryset:
                    
                    expense = expense + x.amount_paid
                
                data.append(
                    {
                        "month":j,
                        "expense":expense
                    }
                )
            
            yearwise.append(
                {
                    "year":i,
                    "details":data
                }
            )

        return Response(yearwise,status=200)                
        # search = self.request.query_params.get('search', None)
        # if search is not None:
        #     queryset = queryset.filter(Q(title__icontains  =search)|Q(note__icontains  =search))

        
        return queryset

class EmployeeMonthlyExpenseAPI(ListAPIView,CreateAPIView):
    queryset = models.Expense.objects.all()
    serializer_class = serializers.ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def list(self,request,*args,**kwargs):

        if not request.user.is_owner and not request.user.is_employee:
            return Response({"Error":"Access Denied"},status=401)

        if request.user.is_owner:
            instance = models.Owner.objects.get(user=request.user)
        else:
            instance = models.Employee.objects.get(user=request.user)
        
        branchlist = instance.branches.all()
        if kwargs["id"] not in branchlist.values_list('id', flat=True):
        # if kwargs["id"] in instance.branches:
            return Response({"error":"Branch does not belong to the owner/employee"},status=403)

        queryset = self.queryset.filter(library_branch=self.kwargs["id"])

        year = self.request.query_params.get('year', None)
        if year is not None:
            queryset = queryset.filter(date__year = year)

        month = self.request.query_params.get('month', None)
        if month is not None:
            queryset = queryset.filter(date__month = month)

        search = self.request.query_params.get('search', None)
        if search is not None:
            queryset = queryset.filter(Q(title__icontains  =search)|Q(note__icontains  =search))

        from_date = self.request.query_params.get('from_date', None)
        if from_date is not None:
            from_date = datetime.datetime.strptime(from_date, "%Y-%m-%d").date()
            queryset = queryset.filter(date__gte = from_date)
    
        to_date = self.request.query_params.get('to_date', None)
        if to_date is not None:
            to_date = datetime.datetime.strptime(to_date, "%Y-%m-%d").date()
            queryset = queryset.filter(date__lte = to_date)

        queryset = queryset.order_by('-date')

        serializer = self.serializer_class(queryset,many=True)

        return Response(serializer.data,status=200)

class StudentPendingsAPI(ListAPIView):
    queryset = studentmodels.PurchasedSubscription.objects.all()
    serializer_class = studentserializers.StudentManageSubSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def get_queryset(self):

        queryset = self.queryset.filter(student__library_branch=self.kwargs["id"])

        search = self.request.query_params.get('search', None)
        if search is not None:
            queryset = queryset.filter(Q(student__name__icontains  =search)|Q(student__id__icontains  =search))
        
        from_date = self.request.query_params.get('from_Date', None)
        if from_date is not None:
            from_date = datetime.datetime.strptime(from_date, "%Y-%m-%d").date()
            queryset = queryset.filter(date__gte = from_date)

        to_date = self.request.query_params.get('to_date', None)
        if to_date is not None:
            to_date = datetime.datetime.strptime(to_date, "%Y-%m-%d").date()
            queryset = queryset.filter(date__lte = to_date)

        queryset = queryset.order_by('student__name')

        return queryset

    def list(self,request,*args,**kwargs):

        if not request.user.is_owner and not request.user.is_employee:
            return Response({"Error":"Access Denied"},status=401)

        if request.user.is_owner:
            instance = models.Owner.objects.get(user=request.user)
        else:
            instance = models.Employee.objects.get(user=request.user)
        
        branchlist = instance.branches.all()
        if self.kwargs["id"] not in branchlist.values_list('id', flat=True):
        # if kwargs["id"] in instance.branches:
            return Response({"error":"Branch does not belong to the owner/employee"},status=403)
        
        queryset = self.get_queryset()

        serializer = self.serializer_class(queryset,many=True)

        return Response(serializer.data,status=200)

class StudentPendingCountAPI(APIView):
    queryset = studentmodels.PurchasedSubscription.objects.all()
    permission_classes = [permissions.IsAuthenticated, ]

    def get(self,request,id):

        if not request.user.is_owner and not request.user.is_employee:
            return Response({"Error":"Access Denied"},status=401)

        if request.user.is_owner:
            instance = models.Owner.objects.get(user=request.user)
        else:
            instance = models.Employee.objects.get(user=request.user)
        
        branchlist = instance.branches.all()
        if self.kwargs["id"] not in branchlist.values_list('id', flat=True):
        # if kwargs["id"] in instance.branches:
            return Response({"error":"Branch does not belong to the owner/employee"},status=403)

        queryset = self.queryset.filter(student__library_branch=self.kwargs["id"])

        return Response({"count":queryset.count()},status=200)