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

class OwnerExpenseMonthlyAPI(ListAPIView):

    queryset = models.Expense.objects.all()
    serializer_class = serializers.OnwerExpenseSerializer
    permission_classes = [permissions.IsAuthenticated, ] 

    def list(self,request,*args,**kwargs):
        today = datetime.date.today()
        queryset = self.queryset.filter(library_branch=kwargs["id"],date__month=today.month)
        search = self.request.query_params.get('search', None)
        if search is not None:
            queryset = queryset.filter(title__icontains  = search)
            
        from_date = self.request.query_params.get('from_date', None)
        to_date = self.request.query_params.get('to_date', None)

        if from_date is not None:
            from_date = datetime.datetime.strptime(from_date, "%Y-%m-%d").date()
            queryset = queryset.filter(date__gte=from_date)

        if to_date is not None:
            to_date = datetime.datetime.strptime(to_date, "%Y-%m-%d").date()
            queryset = queryset.filter(date__lte=to_date)
        serializer = self.serializer_class(queryset,many=True)

        return Response(serializer.data)

class OnwerMonthlyIncomeAPI(ListAPIView):

    queryset = studentmodels.StudentPayment.objects.all()
    serializer_class = studentserializers.StudentPaymentSerializer
    permission_classes = [permissions.IsAuthenticated, ] 

    def list(self,request,*args,**kwargs):
        today = datetime.date.today()

        queryset = self.queryset.filter(purchased_subscription__student__library_branch=kwargs["id"],date__month=today.month)
        search = self.request.query_params.get('search', None)
        if search is not None:
            queryset = queryset.filter(title__icontains  = search)

        from_date = self.request.query_params.get('from_date', None)
        to_date = self.request.query_params.get('to_date', None)

        if from_date is not None:
            from_date = datetime.datetime.strptime(from_date, "%Y-%m-%d").date()
            queryset = queryset.filter(date__gte=from_date)
        if to_date is not None:
            to_date = datetime.datetime.strptime(to_date, "%Y-%m-%d").date()
            queryset = queryset.filter(date__lte=to_date)

        serializer = self.serializer_class(queryset,many=True)

        return Response(serializer.data)

class OwnerExtraIncomeAPI(APIView):

    permission_classes = [permissions.IsAuthenticated, ]

    def get(self,request):

        try:
            owner = models.Owner.objects.get(user=request.user)
        except ObjectDoesNotExist:
            return Response ({"error":"User is not an owner"},status=400)

        queryset = librarymodels.LibraryBranch.objects.filter(library=owner.library)
        search = self.request.query_params.get('search', None)
        if search is not None:
            queryset = queryset.filter(name__icontains  = search)
        #serializer = self.serializer_class(queryset,many=True) 
        data=[]
        today = datetime.date.today()
        for librarybranch in owner.branches.all():
            income = 0
            lastincome = 0
            incomes = studentmodels.StudentUBFPayment.objects.filter(libraryBranch=librarybranch,date__month=today.month,date__year=today.year)
            if today.month==1:
                lastmonth=12
                lastyear=today.year-1
            else:
                lastmonth = today.month-1
                lastyear = today.year
            lastMonth = studentmodels.StudentUBFPayment.objects.filter(libraryBranch=librarybranch,date__month=lastmonth,date__year=lastyear)

            for i in incomes:
                income = income + i.amount_paid

            for i in lastMonth:
                lastincome = lastincome + i.amount_paid
        
            data.append({
                "name":librarybranch.name,
                "id":librarybranch.id,
                "income":income,
                "lastincome":lastincome})

        currenttotal = 0
        lasttotal = 0

        for i in data:
            currenttotal = currenttotal + i["income"]
            lasttotal = lasttotal + i["lastincome"]

        return Response ({
            "currentincome":currenttotal,
            "lasttotal":lasttotal,
            "data":data
        },status=200)

class OwnerExtraIncomeBranchAPI(ListAPIView):
    queryset = studentmodels.StudentUBFPayment.objects.all()
    serializer_class = studentserializers.UBFPaymentSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def list(self,request,*args,**kwargs):

        today = datetime.date.today()

        queryset = self.queryset.filter(libraryBranch=kwargs["id"],date__month=today.month,date__year=today.year)
        if today.month==1:
            lastmonth=12
            lastyear=today.year-1
        else:
            lastmonth = today.month-1
            lastyear = today.year
        lastMonth = self.queryset.filter(libraryBranch=kwargs["id"],date__month=lastmonth,date__year=lastyear)

        currentincome=0
        lastincome=0

        for i in queryset:
            currentincome = currentincome + i.amount_paid
        
        for i in lastMonth:
            lastincome = lastincome + i.amount_paid

        search = self.request.query_params.get('search', None)
        if search is not None:
            queryset = queryset.filter(Q(title__icontains  = search)|Q(student__name__icontains = search))
        
        serializer = self.serializer_class(queryset,many=True)

        return Response({
            "currentincome":currentincome,
            "lastincome":lastincome,
            "data":serializer.data
            },status=200)

class OwnerExpenseAPI(APIView):
    queryset = models.Expense.objects.all()
    serializer_class = serializers.ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def get(self,request,id):
        today = datetime.datetime.today()
        data = []
        yearwise=[]
        try:
            owner = models.Owner.objects.get(user=request.user)
        except ObjectDoesNotExist:
            return Response({"error":"User is not an Owner"},status=401)
        
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
            for i in range(1,today.month+1):
                expense = 0
                
                queryset = self.queryset.filter(library_branch=id,date__month=i,date__year=today.year)

                for j in queryset:
                    
                    expense = expense + j.amount_paid
                
                data.append(
                    {
                        "month":i,
                        "expense":expense
                    }
                )
            
            yearwise.append(
                {
                    "year":today.year,
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
            if startyear == lastyear:
                startmonth = (queryset.first()).date.month
                endmonth = (queryset.last()).date.month
            else:
                startmonth = 1
                endmonth = 12
            for j in range(startmonth,endmonth+1):
                expense = 0

                queryset = self.queryset.filter(library_branch__in=id,date__month=j,date__year=i)

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

class OwnerMonthlyExpenseAPI(ListAPIView,CreateAPIView):
    queryset = models.Expense.objects.all()
    serializer_class = serializers.ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def list(self,request,*args,**kwargs):
        try:
            owner = models.Owner.objects.get(user=request.user)
        except ObjectDoesNotExist:
            return Response({"error":"User is not an Owner"},status=401)
        branch = self.request.query_params.get("branch")

        queryset = self.queryset.filter(library_branch=kwargs["id"])

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

        serializer = self.get_serializer(queryset,many=True)
        # data=[]
        # if branch == "all":
        #     for i in owner.branches.all():
        #         temp=queryset.filter(library_branch=i)
        #         serializer = self.get_serializer(temp,many=True)
        #         data.append({
        #             "branch name":i.name,
        #             "branch id":i.id,
        #             "expense":serializer.data
        #         })
        # else:
        #     temp=queryset.filter(library_branch=int(branch))
        #     serializer = self.get_serializer(temp,many=True)
        #     data.append({
        #         "branch name":i.name,
        #         "branch id":i.id,
        #         "expense":serializer.data
        #     })
        
        return Response(serializer.data,status=200)