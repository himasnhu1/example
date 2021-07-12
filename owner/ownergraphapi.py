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

class WeekwiseProfitAPI(APIView):

    def get(self,request):
        today = datetime.date.today()
        try:
            owner = models.Owner.objects.get(user=request.user)
        except ObjectDoesNotExist:
            return Response({"error":"User is not an Owner"},status=401)
        try:
            ownersub = models.OwnerSubscriptionPlan.objects.get(id=owner.active_subscription.id)
        except ObjectDoesNotExist:
            return Response("No active Subscription",status=400)

        branch = self.request.query_params.get("branch")
        if branch is not None:
            if branch == "all":
                if owner.branches.all().count() != ownersub.activeBranch.all().count():
                    return Response({"Error":"Limited subscription"},status=403)                
                qs1=studentmodels.StudentPayment.objects.none()
                qs2=models.Expense.objects.none()
                qs3=studentmodels.StudentUBFPayment.objects.none()
                for i in owner.branches.all():
                    qs1 = studentmodels.StudentPayment.objects.filter(purchased_subscription__student__library_branch=i) | qs1
                    qs2 = models.Expense.objects.filter(library_branch=i) | qs2
                    qs3 = studentmodels.StudentUBFPayment.objects.filter(libraryBranch=i) | qs3
            else:
                if models.Owner.objects.filter(user=request.user,branches__in=[int(branch)]).exists():
                    pass
                else:
                    return Response({"error":"Branch does not belong to the owner"},status=403)

                branchlist = ownersub.activeBranch.all()
                if int(branch) not in branchlist.values_list('id', flat=True):
                    return Response({"Error":"Branch is not active in current subscription"},status=403)

                qs1 = studentmodels.StudentPayment.objects.filter(purchased_subscription__student__library_branch=int(branch))
                qs2 = models.Expense.objects.filter(library_branch=int(branch))
                qs3 = studentmodels.StudentUBFPayment.objects.filter(libraryBranch=int(branch))
        else:
            return Response({"error":"branch ?branch is required"},status=400)

        month = self.request.query_params.get('month', None)
        year = self.request.query_params.get('year', None)

        if month is not None and year is not None:
            currentMonthIncome = qs1.filter(date__month=int(month),date__year=int(year))
            currentMonthExpense = qs2.filter(date__month=int(month),date__year=int(year))
            currentMonthIncomeExtra = qs3.filter(date__month=int(month),date__year=int(year))
            if int(month)==1:
                lastMonthIncome = qs1.filter(date__month=12,date__year=int(year)-1)
                lastMonthExpense = qs2.filter(date__month=12,date__year=int(year)-1)
                lastMonthIncomeExtra = qs3.filter(date__month=12,date__year=today.year-1)
            else:
                lastMonthIncome = qs1.filter(date__month=int(month)-1,date__year=int(year))
                lastMonthExpense = qs2.filter(date__month=int(month)-1,date__year=int(year))
                lastMonthIncomeExtra = qs3.filter(date__month=int(month)-1,date__year=int(year))
        
        elif month is not None and year is None:
            currentMonthIncome = qs1.filter(date__month=int(month),date__year=today.year)
            currentMonthExpense = qs2.filter(date__month=int(month),date__year=today.year)
            currentMonthIncomeExtra = qs3.filter(date__month=int(month),date__year=today.year)
            if int(month)==1:
                lastMonthIncome = qs1.filter(date__month=12,date__year=today.year-1)
                lastMonthExpense = qs2.filter(date__month=12,date__year=today.year-1)
                lastMonthIncomeExtra = qs3.filter(date__month=12,date__year=today.year-1)
            else:
                lastMonthIncome = qs1.filter(date__month=int(month)-1,date__year=today.year)
                lastMonthExpense = qs2.filter(date__month=int(month)-1,date__year=today.year)
                lastMonthIncomeExtra = qs3.filter(date__month=int(month)-1,date__year=today.year)

        elif month is None and year is not None:
            currentMonthIncome = qs1.filter(date__month=today.month,date__year=int(year))
            currentMonthExpense = qs2.filter(date__month=today.month,date__year=int(year))
            currentMonthIncomeExtra = qs3.filter(date__month=today.month,date__year=int(year))
            if today.month==1:
                lastMonthIncome = qs1.filter(date__month=12,date__year=int(year)-1)
                lastMonthExpense = qs2.filter(date__month=12,date__year=int(year)-1)
                lastMonthIncomeExtra = qs3.filter(date__month=12,date__year=int(year)-1)
            else:
                lastMonthIncome = qs1.filter(date__month=today.month-1,date__year=int(year))
                lastMonthExpense = qs2.filter(date__month=today.month-1,date__year=int(year))
                lastMonthIncomeExtra = qs3.filter(date__month=today.month-1,date__year=int(year))
        else:
            currentMonthIncome = qs1.filter(date__month=today.month,date__year=today.year)
            currentMonthExpense = qs2.filter(date__month=today.month,date__year=today.year)
            currentMonthIncomeExtra = qs3.filter(date__month=today.month,date__year=today.year)
            if today.month==1:
                lastMonthIncome = qs1.filter(date__month=12,date__year=today.year-1)
                lastMonthExpense = qs2.filter(date__month=12,date__year=today.year-1)
                lastMonthIncomeExtra = qs3.filter(date__month=12,date__year=today.year-1)
            else:
                lastMonthIncome = qs1.filter(date__month=today.month-1,date__year=today.year)
                lastMonthExpense = qs2.filter(date__month=today.month-1,date__year=today.year)
                lastMonthIncomeExtra = qs3.filter(date__month=today.month-1,date__year=today.year)

        data = []
        week1=[]
        week2=[]
        week3=[]
        week4=[]
        week5=[]
        #week1
        extraIncome=0
        lastMonthextraIncome=0
        weekIncome=0
        weekExpense = 0
        lastMonthweekIncome=0
        lastMonthweekExpense = 0
        for i in currentMonthIncome.filter(date__day__gte=1,date__day__lte=7):
            weekIncome = weekIncome+int(i.amount_paid)
        for i in currentMonthExpense.filter(date__day__gte=1,date__day__lte=7):
            weekExpense = weekExpense + int(i.amount_paid)
        for i in lastMonthIncome.filter(date__day__gte=1,date__day__lte=7):
            lastMonthweekIncome = lastMonthweekIncome+int(i.amount_paid)
        for i in lastMonthExpense.filter(date__day__gte=1,date__day__lte=7):
            lastMonthweekExpense =lastMonthweekExpense+ int(i.amount_paid)
        for i in currentMonthIncomeExtra.filter(date__day__gte=1,date__day__lte=7):
            extraIncome = extraIncome+int(i.amount_paid)
        for i in lastMonthIncomeExtra.filter(date__day__gte=1,date__day__lte=7):
            lastMonthextraIncome =lastMonthextraIncome+ int(i.amount_paid)
        week1={
            "week":1,
            "currentmonthprofit":extraIncome+weekIncome-weekExpense,
            "lastmonthprofit":lastMonthextraIncome + lastMonthweekIncome - lastMonthweekExpense
        }
        data.append(week1)
        #week2
        weekIncome=0
        weekExpense = 0
        lastMonthweekIncome=0
        lastMonthweekExpense = 0
        for i in currentMonthIncome.filter(date__day__gte=8,date__day__lte=14):
            weekIncome = weekIncome+int(i.amount_paid)
        for i in currentMonthExpense.filter(date__day__gte=8,date__day__lte=14):
            weekExpense = weekExpense + int(i.amount_paid)
        for i in lastMonthIncome.filter(date__day__gte=8,date__day__lte=14):
            lastMonthweekIncome = lastMonthweekIncome+int(i.amount_paid)
        for i in lastMonthExpense.filter(date__day__gte=8,date__day__lte=14):
            lastMonthweekExpense =lastMonthweekExpense+ int(i.amount_paid)
        for i in currentMonthIncomeExtra.filter(date__day__gte=8,date__day__lte=14):
            extraIncome = extraIncome+int(i.amount_paid)
        for i in lastMonthIncomeExtra.filter(date__day__gte=8,date__day__lte=14):
            lastMonthextraIncome =lastMonthextraIncome+ int(i.amount_paid)
        week2={
            "week":2,
            "currentmonthprofit":extraIncome+weekIncome-weekExpense,
            "lastmonthprofit":lastMonthextraIncome + lastMonthweekIncome - lastMonthweekExpense
        }
        data.append(week2)
        #week3
        weekIncome=0
        weekExpense = 0
        lastMonthweekIncome=0
        lastMonthweekExpense = 0
        for i in currentMonthIncome.filter(date__day__gte=15,date__day__lte=21):
            weekIncome = weekIncome+int(i.amount_paid)
        for i in currentMonthExpense.filter(date__day__gte=15,date__day__lte=21):
            weekExpense = weekExpense + int(i.amount_paid)
        for i in lastMonthIncome.filter(date__day__gte=15,date__day__lte=21):
            lastMonthweekIncome = lastMonthweekIncome+int(i.amount_paid)
        for i in lastMonthExpense.filter(date__day__gte=15,date__day__lte=21):
            lastMonthweekExpense =lastMonthweekExpense+ int(i.amount_paid)
        for i in currentMonthIncomeExtra.filter(date__day__gte=15,date__day__lte=21):
            extraIncome = extraIncome+int(i.amount_paid)
        for i in lastMonthIncomeExtra.filter(date__day__gte=15,date__day__lte=21):
            lastMonthextraIncome =lastMonthextraIncome+ int(i.amount_paid)
        week3={
            "week":3,
            "currentmonthprofit":extraIncome+weekIncome-weekExpense,
            "lastmonthprofit":lastMonthextraIncome + lastMonthweekIncome - lastMonthweekExpense
        }
        data.append(week3)
        #week 4
        weekIncome=0
        weekExpense = 0
        lastMonthweekIncome=0
        lastMonthweekExpense = 0
        for i in currentMonthIncome.filter(date__day__gte=22,date__day__lte=28):
            weekIncome = weekIncome+int(i.amount_paid)
        for i in currentMonthExpense.filter(date__day__gte=22,date__day__lte=28):
            weekExpense = weekExpense + int(i.amount_paid)
        for i in lastMonthIncome.filter(date__day__gte=22,date__day__lte=28):
            lastMonthweekIncome = lastMonthweekIncome+int(i.amount_paid)
        for i in lastMonthExpense.filter(date__day__gte=22,date__day__lte=28):
            lastMonthweekExpense =lastMonthweekExpense+ int(i.amount_paid)
        week4={
            "week":4,
            "currentmonthprofit":extraIncome+weekIncome-weekExpense,
            "lastmonthprofit":lastMonthextraIncome + lastMonthweekIncome - lastMonthweekExpense
        }
        data.append(week4)
        #week5
        weekIncome=0
        weekExpense = 0
        lastMonthweekIncome=0
        lastMonthweekExpense = 0
        for i in currentMonthIncome.filter(date__day__gte=29,date__day__lte=31):
            weekIncome = weekIncome+int(i.amount_paid)
        for i in currentMonthExpense.filter(date__day__gte=29,date__day__lte=31):
            weekExpense = weekExpense + int(i.amount_paid)
        for i in lastMonthIncome.filter(date__day__gte=29,date__day__lte=31):
            lastMonthweekIncome = lastMonthweekIncome+int(i.amount_paid)
        for i in lastMonthExpense.filter(date__day__gte=29,date__day__lte=31):
            lastMonthweekExpense =lastMonthweekExpense+ int(i.amount_paid)
        for i in currentMonthIncomeExtra.filter(date__day__gte=29,date__day__lte=31):
            extraIncome = extraIncome+int(i.amount_paid)
        for i in lastMonthIncomeExtra.filter(date__day__gte=29,date__day__lte=31):
            lastMonthextraIncome =lastMonthextraIncome+ int(i.amount_paid)
        week5={
            "week":5,
            "currentmonthprofit":extraIncome + weekIncome-weekExpense,
            "lastmonthprofit":lastMonthextraIncome + lastMonthweekIncome - lastMonthweekExpense
        }
        data.append(week5)

        return Response(data,status=200)

class WeekwiseIncomeExpenseAPI(APIView):  ##adding ubf income also  date:30-10-10   #weekwise graph data output list of expense and income

    def get(self,request):
        today = datetime.date.today()
        try:
            owner = models.Owner.objects.get(user=request.user)
        except ObjectDoesNotExist:
            return Response({"error":"User is not an Owner"},status=401)

        qs1 = studentmodels.StudentPayment.objects.all()
        qs2 = models.Expense.objects.all()

        branch = self.request.query_params.get("branch")
        if branch is not None:
            qs1 = studentmodels.StudentPayment.objects.filter(purchased_subscription__student__library_branch=int(branch))
            qs2 = models.Expense.objects.filter(library_branch=int(branch))
            qs3 = studentmodels.StudentUBFPayment.objects.filter(libraryBranch=int(branch))

        week = self.request.query_params.get("week")
        month = self.request.query_params.get("month")
        if month is not None :
            currentMonthIncome = qs1.filter(date__month=int(month),date__year=today.year)
            currentMonthExpense = qs2.filter(date__month=int(month),date__year=today.year)
            currentMonthIncomeExtra = qs3.filter(date__month=today.month,date__year=today.year)
            if int(month)==1:
                lastMonthIncome = qs1.filter(date__month=12,date__year=today.year-1)
                lastMonthExpense = qs2.filter(date__month=12,date__year=today.year-1)
                lastMonthIncomeExtra = qs3.filter(date__month=12,date__year=today.year-1)
            else:
                lastMonthIncome = qs1.filter(date__month=int(month)-1,date__year=today.year)
                lastMonthExpense = qs2.filter(date__month=int(month)-1,date__year=today.year)
                lastMonthIncomeExtra = qs3.filter(date__month=int(month)-1,date__year=today.year)

        if week is not None:
            if week == "week1":
                currentMonthIncome = currentMonthIncome.filter(date__day__gte=1,date__day__lte=7)
                currentMonthExpense = currentMonthExpense.filter(date__day__gte=1,date__day__lte=7)
                lastMonthIncome = lastMonthIncome.filter(date__day__gte=1,date__day__lte=7)
                lastMonthExpense = lastMonthExpense.filter(date__day__gte=1,date__day__lte=7)
                currentMonthIncomeExtra = currentMonthIncomeExtra.filter(date__day__gte=1,date__day__lte=7)
                lastMonthIncomeExtra = lastMonthIncomeExtra.filter(date__day__gte=1,date__day__lte=7)
            elif week=='week2':
                currentMonthIncome = currentMonthIncome.filter(date__day__gte=8,date__day__lte=14)
                currentMonthExpense = currentMonthExpense.filter(date__day__gte=8,date__day__lte=14)
                lastMonthIncome = lastMonthIncome.filter(date__day__gte=8,date__day__lte=14)
                lastMonthExpense = lastMonthExpense.filter(date__day__gte=8,date__day__lte=14)
                currentMonthIncomeExtra = currentMonthIncomeExtra.filter(date__day__gte=8,date__day__lte=14)
                lastMonthIncomeExtra = lastMonthIncomeExtra.filter(date__day__gte=8,date__day__lte=14)
            elif week=='week3':
                currentMonthIncome = currentMonthIncome.filter(date__day__gte=15,date__day__lte=21)
                currentMonthExpense = currentMonthExpense.filter(date__day__gte=15,date__day__lte=21)
                lastMonthIncome = lastMonthIncome.filter(date__day__gte=15,date__day__lte=21)
                lastMonthExpense = lastMonthExpense.filter(date__day__gte=15,date__day__lte=21)
                currentMonthIncomeExtra = currentMonthIncomeExtra.filter(date__day__gte=15,date__day__lte=21)
                lastMonthIncomeExtra = lastMonthIncomeExtra.filter(date__day__gte=15,date__day__lte=21)
            elif week=='week4':
                currentMonthIncome = currentMonthIncome.filter(date__day__gte=22,date__day__lte=28)
                currentMonthExpense = currentMonthExpense.filter(date__day__gte=22,date__day__lte=28)
                lastMonthIncome = lastMonthIncome.filter(date__day__gte=22,date__day__lte=28)
                lastMonthExpense = lastMonthExpense.filter(date__day__gte=22,date__day__lte=28)
                currentMonthIncomeExtra = currentMonthIncomeExtra.filter(date__day__gte=22,date__day__lte=28)
                lastMonthIncomeExtra = lastMonthIncomeExtra.filter(date__day__gte=22,date__day__lte=28)
            elif week=='week5':
                currentMonthIncome = currentMonthIncome.filter(date__day__gte=29,date__day__lte=31)
                currentMonthExpense = currentMonthExpense.filter(date__day__gte=29,date__day__lte=31)
                lastMonthIncome = lastMonthIncome.filter(date__day__gte=29,date__day__lte=31)
                lastMonthExpense = lastMonthExpense.filter(date__day__gte=29,date__day__lte=31)
                currentMonthIncomeExtra = currentMonthIncomeExtra.filter(date__day__gte=29,date__day__lte=31)
                lastMonthIncomeExtra = lastMonthIncomeExtra.filter(date__day__gte=29,date__day__lte=31)                
        
        search = self.request.query_params.get('search', None)
        if search is not None:
            currentMonthIncome = currentMonthIncome.filter(title__icontains  = search)
            lastMonthIncome = lastMonthIncome.filter(title__icontains  = search)
            currentMonthExpense = currentMonthExpense.filter(title__icontains  = search)
            lastMonthExpense = lastMonthExpense.filter(title__icontains  = search)
            currentMonthIncomeExtra = currentMonthIncomeExtra.filter(title__icontains  = search)
            lastMonthIncomeExtra = lastMonthIncomeExtra.filter(title__icontains  = search)

        serializer1 = serializers.OnwerExpenseListSerializer(currentMonthExpense,many=True)
        serializer2 = serializers.OnwerExpenseListSerializer(lastMonthExpense,many=True)
        serializer3 = studentserializers.StudentPaymentSerializer(currentMonthIncome,many=True)
        serializer4 = studentserializers.StudentPaymentSerializer(lastMonthIncome,many=True)
        serializer5 = studentserializers.UBFPaymentSerializer(currentMonthIncomeExtra,many=True)
        serializer6 = studentserializers.UBFPaymentSerializer(lastMonthIncomeExtra,many=True)

        data={
            "currentMonthIncome":serializer3.data,
            "lastMonthIncome":serializer4.data,
            "currentMonthExpense":serializer1.data,
            "lastMonthExpense":serializer2.data,
            "currentMonthIncomeExtra":serializer5.data,
            "lastMonthIncomeExtra":serializer6.data
        }

        return Response(data,status=200)

class OwnerGraphIncomeExpenseFilterAPI(APIView):  #adding ubf income also -date:30-10-20
    
    permission_classes = [permissions.IsAuthenticated, ] 

    def get(self,request):
        today = datetime.date.today()
        if not request.user.is_owner:
            return Response({"error":"User is not an owner"},status=400)
        owner = models.Owner.objects.get(user=request.user)

        try:
            ownersub = models.OwnerSubscriptionPlan.objects.get(id=owner.active_subscription.id)
        except ObjectDoesNotExist:
            return Response("No active Subscription",status=400)

        id = self.request.query_params.get('branch', None)
        if id is not None:
            if id=='all':
                if owner.branches.all().count() != ownersub.activeBranch.all().count():
                    return Response({"Error":"Limited subscription"},status=403) 

                qs1 = studentmodels.StudentPayment.objects.filter(purchased_subscription__student__library_branch__library=owner.library)
                qs2 = models.Expense.objects.filter(library_branch__library=owner.library)
                qs3 = studentmodels.StudentUBFPayment.objects.filter(libraryBranch__library=owner.library)
            else:
                if models.Owner.objects.filter(user=request.user,branches__in=[int(id)]).exists():
                    pass
                else:
                    return Response({"error":"Branch does not belong to the owner"},status=403)

                branchlist = ownersub.activeBranch.all()
                if int(id) not in branchlist.values_list('id', flat=True):
                    return Response({"Error":"Branch is not active in current subscription"},status=403)

                qs1 = studentmodels.StudentPayment.objects.filter(purchased_subscription__student__library_branch=int(id))
                qs2 = models.Expense.objects.filter(library_branch=int(id))
                qs3 = studentmodels.StudentUBFPayment.objects.filter(libraryBranch=int(id))  
        else:
            return Response({"error":"branch ?branch is required"},status=400)  

        currentMonthIncome = qs1.filter(date__month=today.month,date__year=today.year)
        currentMonthExpense = qs2.filter(date__month=today.month,date__year=today.year)
        currentMonthIncomeExtra = qs3.filter(date__month=today.month,date__year=today.year)
        if today.month==1:
            lastMonthIncome = qs1.filter(date__month=12,date__year=today.year-1)
            lastMonthExpense = qs2.filter(date__month=12,date__year=today.year-1)
            lastMonthIncomeExtra = qs3.filter(date__month=12,date__year=today.year-1)
        else:
            lastMonthIncome = qs1.filter(date__month=today.month-1,date__year=today.year)
            lastMonthExpense = qs2.filter(date__month=today.month-1,date__year=today.year)
            lastMonthIncomeExtra = qs3.filter(date__month=today.month-1,date__year=today.year)

        CurrentIncome=0
        LastIncome = 0
        CurrentExpense=0
        LastExpense = 0

        for i in currentMonthIncome:
            CurrentIncome = CurrentIncome +int (i.amount_paid) 
        for i in lastMonthIncome:
            LastIncome = LastIncome +int (i.amount_paid)
        for i in currentMonthExpense:
            CurrentExpense = CurrentExpense +int (i.amount_paid)
        for i in lastMonthExpense:
            LastExpense = LastExpense +int (i.amount_paid)
        for i in currentMonthIncomeExtra:
            CurrentIncome = CurrentIncome + int(i.amount_paid)
        for i in lastMonthIncomeExtra:
            LastIncome = LastIncome + int(i.amount_paid)
        if id !='all':
            library_branch = librarymodels.LibraryBranch.objects.get(id=int(id))
            name = library_branch.name
        else:
            name = "all"

        data ={
            "libraryName":name,
            "currentIncome":CurrentIncome,
            "lastIncome":LastIncome,
            "currentExpense":CurrentExpense,
            "lastExpense":LastExpense
        }

        return Response(data,status=200)

class OwnerActivityReportAPI(APIView):
    queryset = studentmodels.Student.objects.all()

    def get(self,request):
        today = datetime.date.today()
        start=today.replace(day=1)
        try:
            owner = models.Owner.objects.get(user=request.user)
        except ObjectDoesNotExist:
            return Response({"error":"User is not owner"},status=400)

        try:
            ownersub = models.OwnerSubscriptionPlan.objects.get(id=owner.active_subscription.id)
        except ObjectDoesNotExist:
            return Response("No active Subscription",status=400)

        id = self.request.query_params.get('branch', None)
        data=[]
        if id is not None:
            if id=='all': 
                if owner.branches.all().count() != ownersub.activeBranch.all().count():
                    return Response({"Error":"Limited subscription"},status=403)  
                queryset = studentmodels.Student.objects.none()
                complains = models.Feedback.objects.none()
                enquiries = models.Enquiry.objects.none()
                for i in owner.branches.all():
                    queryset = self.queryset.filter(library_branch=i) | queryset
                    complains = models.Feedback.objects.filter(library_branch=i,type="Complaint") | complains
                    enquiries = models.Enquiry.objects.filter(library_branch=i) | enquiries
            else:

                if models.Owner.objects.filter(user=request.user,branches__in=[int(id)]).exists():
                    pass
                else:
                    return Response({"error":"Branch does not belong to the owner"},status=403)

                branchlist = ownersub.activeBranch.all()
                if int(id) not in branchlist.values_list('id', flat=True):
                    return Response({"Error":"Branch is not active in current subscription"},status=403)

                queryset = self.queryset.filter(library_branch=int(id))
                complains = models.Feedback.objects.filter(library_branch=int(id),type="Complaint")
                enquiries = models.Enquiry.objects.filter(library_branch=int(id))
        else:
            return Response({"error":"branch ?branch is required"},status=400)

        currentmonth=today.month
        currentyear=today.year

        if (currentmonth==1):
            lastmonth=12
            lastyear=currentyear-1
        else:
            lastmonth = currentmonth-1
            lastyear=today.year

        currentadmission = 0
        lastadmission=0
        currentrenewal = 0
        lastrenewal = 0 
        currentpending =0 
        lastpending = 0

        for student in queryset:
            
            sub = studentmodels.PurchasedSubscription.objects.filter(student=student)
            #lastmonthsub= studentmodels.PurchasedSubscription.objects.filter(student=student,date__lt=start)
            currentmonthsub = studentmodels.PurchasedSubscription.objects.filter(student=student,date__month=currentmonth,date__year=currentyear)
            lastmonthsub = studentmodels.PurchasedSubscription.objects.filter(student=student,date__month=lastmonth,date__year=lastyear)

            if sub.count()==1 and currentmonthsub.count() ==1:
                currentadmission = currentadmission + 1

            elif sub.count()>1 and currentmonthsub.count() >=1:
                currentrenewal = currentrenewal + 1

            if lastmonthsub.count()==1 and lastmonthsub.count() ==1:
                lastadmission = lastadmission + 1

            elif lastmonthsub.count()>1 and lastmonthsub.count() >=1:
                lastrenewal = lastrenewal + 1
            
            total_amount = currentmonthsub.aggregate(Sum('total_amount'))
            total_amount = total_amount['total_amount__sum']
            payments = studentmodels.StudentPayment.objects.filter(purchased_subscription__in=currentmonthsub).aggregate(Sum('amount_paid'))
            payments = payments['amount_paid__sum']
            due = total_amount

            if due is not None:

                if payments:
                    due = total_amount - payments
                
                if due>0:
                    currentpending = currentpending + 1

            total_amount = lastmonthsub.aggregate(Sum('total_amount'))
            total_amount = total_amount['total_amount__sum']
            payments = studentmodels.StudentPayment.objects.filter(purchased_subscription__in=lastmonthsub).aggregate(Sum('amount_paid'))
            payments = payments['amount_paid__sum']
            due = total_amount
            if due is not None:
                if payments:
                    due = total_amount - payments

                if due>0:
                    lastpending = lastpending + 1
        
        
        data={
            "currentadmission": currentadmission,
            "lastadmission":lastadmission,
            "currentrenewal":currentrenewal,
            "lastrenewal":lastrenewal,
            "currentpending":currentpending,
            "lastpending":lastpending,
            "currentcomplains":complains.filter(date__month=currentmonth,date__year=currentyear).count(),
            "lastcomplains":complains.filter(date__month=lastmonth,date__year=lastyear).count(),
            "currentenquiry":enquiries.filter(date__month=currentmonth,date__year=currentyear).count(),
            "lastenquiry":enquiries.filter(date__month=lastmonth,date__year=lastyear).count(),
        }

        return Response(data,status=200)

class OwnerExtraIncomeGraphAPI(APIView):

    permission_classes = [permissions.IsAuthenticated, ]

    def get(self,request):

        try:
            owner = models.Owner.objects.get(user=request.user)
        except ObjectDoesNotExist:
            return Response ({"error":"User is not an owner"},status=400)

        try:
            ownersub = models.OwnerSubscriptionPlan.objects.get(id=owner.active_subscription.id)
        except ObjectDoesNotExist:
            return Response("No active Subscription",status=400)

        id = self.request.query_params.get('branch', None)
        if id is None:
            return Response({"error":"branch ?branch is required"},status=400)
        #serializer = self.serializer_class(queryset,many=True) 
        data=[]
        today = datetime.date.today()
        if id == "all":
            if owner.branches.all().count() != ownersub.activeBranch.all().count():
                return Response({"Error":"Limited subscription"},status=403) 
            branches = owner.branches.all()
        else:
            if models.Owner.objects.filter(user=request.user,branches__in=[int(id)]).exists():
                pass
            else:
                return Response({"error":"Branch does not belong to the owner"},status=403)
            branchlist = ownersub.activeBranch.all()
            if int(id) not in branchlist.values_list('id', flat=True):
                return Response({"Error":"Branch is not active in current subscription"},status=403)

            branches = librarymodels.LibraryBranch.objects.filter(id=int(id))
        for librarybranch in branches:
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
        },status=200)

class MonthlyExpensePointAPI(APIView):  ##adding ubf income also  date:30-10-10   #weekwise graph data output list of expense and income

    def get(self,request):
        today = datetime.date.today()
        qs2 = models.Expense.objects.all()

        try:
            owner = models.Owner.objects.get(user=request.user)
        except ObjectDoesNotExist:
            return Response({"error":"User is not an Owner"},status=401)

        try:
            ownersub = models.OwnerSubscriptionPlan.objects.get(id=owner.active_subscription.id)
        except ObjectDoesNotExist:
            return Response("No active Subscription",status=400)

        id = self.request.query_params.get('branch', None)
        if id is None:
            return Response({"error":"branch ?branch is required"},status=400)
        data=[]
        today = datetime.date.today()
        if id == "all":
            if owner.branches.all().count() != ownersub.activeBranch.all().count():
                return Response({"Error":"Limited subscription"},status=403) 
            queryset = models.Expense.objects.none()
            for i in owner.branches.all():
                queryset = qs2.filter(library_branch=i) | queryset
        else:
            if models.Owner.objects.filter(user=request.user,branches__in=[int(id)]).exists():
                pass
            else:
                return Response({"error":"Branch does not belong to the owner"},status=403)
            branchlist = ownersub.activeBranch.all()
            if int(id) not in branchlist.values_list('id', flat=True):
                return Response({"Error":"Branch is not active in current subscription"},status=403)
            queryset = models.Expense.objects.filter(library_branch=int(id))

        currentmonth = []
        lastmonth = []

        days = [1,5,10,15,20,25,31]

        i = 0
        info=[]
        while i<=6:
            if i == 1:
                current = queryset.filter(date__day=1,date__month=today.month,date__year=today.year)
            else:
                current = queryset.filter(date__day__gt=days[i-1],date__day__lte=days[i],date__month=today.month,date__year=today.year)
            expense =0 
            for j in current:
                expense = expense + j.amount_paid
            
            data.append({str(i):expense})
            i=i+1
        info.append({"currentmonth":data})

        if today.month ==1:
            lastmonth = 12
            lastyear = today.year-1
        else:
            lastmonth = today.month-1
            lastyear = today.year
        data=[]

        i = 0
        while i<=6:
            if i == 1:
                current = queryset.filter(date__day=1,date__month=lastmonth,date__year=lastyear)
            else:
                current = queryset.filter(date__day__gt=days[i-1],date__day__lte=days[i],date__month=lastmonth,date__year=lastyear)
            expense =0 

            for j in current:
                expense = expense + j.amount_paid
            
            data.append({str(i):expense})
            i=i+1
        info.append({"lastmonth":data})

        return Response(info,status=200)


class MonthlyIncomePointAPI(APIView):  ##adding ubf income also  date:30-10-10   #weekwise graph data output list of expense and income

    def get(self,request):
        today = datetime.date.today()
        qs2 = studentmodels.StudentPayment.objects.all()
        qs3 = studentmodels.StudentUBFPayment.objects.all()

        try:
            owner = models.Owner.objects.get(user=request.user)
        except ObjectDoesNotExist:
            return Response({"error":"User is not an Owner"},status=401)

        try:
            ownersub = models.OwnerSubscriptionPlan.objects.get(id=owner.active_subscription.id)
        except ObjectDoesNotExist:
            return Response("No active Subscription",status=400)

        id = self.request.query_params.get('branch', None)
        if id is None:
            return Response({"error":"branch ?branch is required"},status=400)
        data=[]
        today = datetime.date.today()
        if id == "all":
            if owner.branches.all().count() != ownersub.activeBranch.all().count():
                return Response({"Error":"Limited subscription"},status=403) 
            queryset = studentmodels.StudentPayment.objects.none()
            queryset1 = studentmodels.StudentUBFPayment.objects.none()
            for i in owner.branches.all():
                queryset = qs2.filter(purchased_subscription__student__library_branch=i) | queryset
                queryset1 = qs3.filter(student__library_branch=i) | queryset1
        else:
            if models.Owner.objects.filter(user=request.user,branches__in=[int(id)]).exists():
                pass
            else:
                return Response({"error":"Branch does not belong to the owner"},status=403)
            branchlist = ownersub.activeBranch.all()
            if int(id) not in branchlist.values_list('id', flat=True):
                return Response({"Error":"Branch is not active in current subscription"},status=403)
            queryset = studentmodels.StudentPayment.objects.filter(purchased_subscription__student__library_branch=int(id))
            queryset1 = studentmodels.StudentUBFPayment.objects.filter(student__library_branch=int(id))

        currentmonth = []
        lastmonth = []

        days = [1,5,10,15,20,25,31]

        i = 0
        info=[]
        while i<=6:
            if i == 1:
                current = queryset.filter(date__day=1,date__month=today.month,date__year=today.year)
                extracurrent = queryset1.filter(date__day=1,date__month=today.month,date__year=today.year)
            else:
                current = queryset.filter(date__day__gt=days[i-1],date__day__lte=days[i],date__month=today.month,date__year=today.year)
                extracurrent = queryset1.filter(date__day__gt=days[i-1],date__day__lte=days[i],date__month=today.month,date__year=today.year)
            income =0 
            for j in current:
                income = income + j.amount_paid

            for j in extracurrent:
                income = income + j.amount_paid
            
            data.append({str(i):income})
            i=i+1
        info.append({"currentmonth":data})

        if today.month ==1:
            lastmonth = 12
            lastyear = today.year-1
        else:
            lastmonth = today.month-1
            lastyear = today.year
        data=[]

        i = 0
        while i<=6:
            if i == 1:
                current = queryset.filter(date__day=1,date__month=lastmonth,date__year=lastyear)
                extracurrent = queryset1.filter(date__day=1,date__month=lastmonth,date__year=lastyear)
            else:
                current = queryset.filter(date__day__gt=days[i-1],date__day__lte=days[i],date__month=lastmonth,date__year=lastyear)
                extracurrent = queryset1.filter(date__day__gt=days[i-1],date__day__lte=days[i],date__month=lastmonth,date__year=lastyear)
            income =0 

            for j in current:
                income = income + j.amount_paid

            for j in extracurrent:
                income = income + j.amount_paid
            
            data.append({str(i):income})
            i=i+1
        info.append({"lastmonth":data})

        return Response(info,status=200)


class StudentList(ListAPIView):
    queryset = studentmodels.Student.objects.all()
    serializer_class = studentserializers.StudentListSerializer
    permission_classes = [permissions.IsAuthenticated,]

    def list(self,request,*args,**kwargs):
        try:
            owner = models.Owner.objects.get(user=request.user)
        except ObjectDoesNotExist:
            return Response({"error":"User is not an Owner"},status=401)

        if models.Owner.objects.filter(user=request.user,branches__in=[int(kwargs["id"])]).exists():
            pass
        else:
            return Response({"error":"Branch does not belong to the owner"},status=403)
        
        queryset = self.queryset.filter(library_branch=kwargs["id"])

        search = self.request.query_params.get('search',None)
        if search is not None:
            queryset = queryset.filter(name__icontains=search)

        queryset = queryset.order_by("id")

        serializer = self.serializer_class(queryset,many=True)

        return Response(serializer.data,status=200)