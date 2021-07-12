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

import pandas as pd
from sklearn import linear_model


class PotentialRevenueMonthlyAPI(APIView):

    def get(self,request):
        today = datetime.date.today()
        owner = models.Owner.objects.get(user=request.user)
        id = self.request.query_params.get('branch', None)
        if id is not None:
            if id=='all':
                qs1 = studentmodels.StudentPayment.objects.filter(purchased_subscription__student__library_branch__library=owner.library)
                #qs2 = models.Expense.objects.filter(library_branch__library=owner.library)
                qs3 = studentmodels.StudentUBFPayment.objects.filter(library_branch__library=owner.library)
            else:
                qs1 = studentmodels.StudentPayment.objects.filter(purchased_subscription__student__library_branch=int(id)).order_by("date")
                #qs2 = models.Expense.objects.filter(library_branch=int(id))
                qs3 = studentmodels.StudentUBFPayment.objects.filter(libraryBranch=int(id)).order_by("date")
        date = qs1[0].date
        data=[]        
        for i in range(date.year,today.year+1):
            if i==today.year:
                months = today.month-1
            else:
                months=12      
            for j in range(1,months+1):
                income = 0
                currentMonthIncome = qs1.filter(date__month=j,date__year=i)
                if currentMonthIncome.count() >0:
                    for x in currentMonthIncome:
                        income = income + x.amount_paid
                currentMonthIncomeExtra = qs3.filter(date__month=j,date__year=i)
                if currentMonthIncomeExtra.count() >0:
                    for x in currentMonthIncomeExtra:
                        income = income + x.amount_paid
                if currentMonthIncome.count() >0 or currentMonthIncomeExtra.count() >0:
                    data.append({
                        "month":j,
                        "year":i,
                        "income":income
                    })
        # currentMonthIncome = qs1.filter(date__month=today.month,date__year=today.year)
        # currentMonthExpense = qs2.filter(date__month=today.month,date__year=today.year)
        # currentMonthIncomeExtra = qs3.filter(date__month=today.month,date__year=today.year)
        # if today.month==1:
        #     lastMonthIncome = qs1.filter(date__month=12,date__year=today.year-1)
        #     lastMonthExpense = qs2.filter(date__month=12,date__year=today.year-1)
        #     lastMonthIncomeExtra = qs3.filter(date__month=12,date__year=today.year-1)
        # else:
        #     lastMonthIncome = qs1.filter(date__month=today.month-1,date__year=today.year)
        #     lastMonthExpense = qs2.filter(date__month=today.month-1,date__year=today.year)
        #     lastMonthIncomeExtra = qs3.filter(date__month=today.month-1,date__year=today.year)
        income = 0
        currentMonthIncome = qs1.filter(date__month=today.month,date__year=today.year)
        for x in currentMonthIncome:
            income = income + x.amount_paid
        currentMonthIncomeExtra = qs3.filter(date__month=today.month,date__year=today.year)
        for x in currentMonthIncomeExtra:
            income = income + x.amount_paid
        df =pd.DataFrame(data)
        X = df[['month', 'year']]
        y = df['income']
        regr = linear_model.LinearRegression()
        regr.fit(X, y)
        predictedIncome = regr.predict([[today.month, today.year]])
        # print (df)
        # print(predictedIncome)
        return Response({"potentialIncome":predictedIncome[0],"CurrentMonthIncome":income},status=200)