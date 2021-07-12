from django.shortcuts import render
from . import models, serializers
from rest_framework import viewsets, status, permissions
import datetime
from rest_framework.decorators import action
from django.db.models import Q
from rest_framework.response import Response

from django.http import HttpResponse
from library import models as librarymodels
from library import serializers as libraryserializers
from django.core.exceptions import ObjectDoesNotExist
from owner import models as ownermodels

from core import models as coremodels
from core import serializers as coreserializers
from rest_framework.views import APIView

from rest_framework.generics import *
import ast
import csv

from django.core.mail import EmailMessage
from io import StringIO
class StudentAPIViewSet(ListAPIView,UpdateAPIView):
    queryset = models.Student.objects.all()
    serializer_class = serializers.StudentMinSerializer
    permission_classes = [permissions.IsAuthenticated, ]

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

        queryset = self.queryset.filter(library_branch=self.kwargs["id"])
        active = self.request.query_params.get('active', None)
        if active is not None:
            if active=="true":
                queryset = queryset.filter(active_subscription__active=True)
            else:
                queryset = queryset.filter(Q(active_subscription__active=False)|Q(active_subscription__isnull=True))

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
            queryset = queryset.filter(Q(name__icontains  =search)|Q(email__icontains  =search))

        queryset = queryset.order_by('name')
        serializer = self.get_serializer(queryset,many=True)

        return Response(serializer.data,status=200)

    def partial_update(self,request,*args,**kwargs):

        if not request.user.is_owner and not request.user.is_employee:
            return Response({"error":"User is not an owner/employee"},status=401)
        
        if request.user.is_owner:
            instance = models.Owner.objects.get(user = request.user)
        elif request.user.is_employee:
            instance = models.Employee.objects.get(user = request.user)
        
        branchlist = instance.branches.all()
        if int(id) not in branchlist.values_list('id', flat=True):
            return Response({"Error":"Branch does not belong to this owner/employee"},status=403) 

        student = self.queryset.get(id=request.data["objId"])
        sub = models.PurchasedSubscription.objects.filter(student_id=student.id)
        latestSub = sub.latest('date')
        if request.data["active"]  == True or request.data["active"]=="true":
            
            if request.data["change"]== False or request.data["change"]=="false":
                latestSub.pk=None
                latestSub.due_date=datetime.datetime.today()+datetime.timedelta(days=latestSub.days)
                latestSub.active=True
                latestSub.from_date=datetime.datetime.today()
                latestSub.save()
                student.active_subscription = latestSub
        elif request.data["active"] == False or request.data["active"]=="false":
            latestSub.active=False
            latestSub.due_date=datetime.datetime.today()
            student.active_subscription = None
            latestSub.save()
        # serializer = serializers.PurchasedSubscriptionSerializer(latestSub,data=request.data,partial=True)
        # serializer.is_valid(raise_exception=True)
        # serializer.save()
        student.save()
        return Response("Successfully Updated",status=200)

class StudentCornerDetailAPI(RetrieveUpdateAPIView):

    queryset = models.Student.objects.all()
    serializer_class = serializers.StudentSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def retrieve(self,request,*args,**kwargs):

        if not request.user.is_owner and not request.user.is_employee:
            return Response({"error":"User is not an owner/employee"},status=401)
        
        if request.user.is_owner:
            instance = models.Owner.objects.get(user = request.user)
        elif request.user.is_employee:
            instance = models.Employee.objects.get(user = request.user)
        
        branchlist = instance.branches.all()
        if int(id) not in branchlist.values_list('id', flat=True):
            return Response({"Error":"Branch does not belong to this owner/employee"},status=403) 

        student = self.queryset.get(id=self.kwargs['pk'])
        serializer = self.serializer_class(student)
        return Response(serializer.data)

    def partial_update(self,request,*args,**kwargs):

        if not request.user.is_owner and not request.user.is_employee:
            return Response({"error":"User is not an owner/employee"},status=401)
        
        if request.user.is_owner:
            instance = models.Owner.objects.get(user = request.user)
        elif request.user.is_employee:
            instance = models.Employee.objects.get(user = request.user)
        
        branchlist = instance.branches.all()
        if int(id) not in branchlist.values_list('id', flat=True):
            return Response({"Error":"Branch does not belong to this owner/employee"},status=403) 

        student = self.queryset.get(id=self.kwargs['pk'])

        if 'exam_preparing_for' in request.data:
            if request.data['source'] == 'flutter':
                request.data['exam_preparing_for'] =  ast.literal_eval(request.data['exam_preparing_for'])
                request.data['exam_preparing_for'] = request.data['exam_preparing_for'][0]
            elif request.data['source'] == 'web':
                request.data['exam_preparing_for'] =  ast.literal_eval(request.data['exam_preparing_for']) 
        serializer = self.serializer_class(student,data=request.data,partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=200)
class StudentDetailAPI(RetrieveUpdateAPIView):

    queryset = models.Student.objects.all()
    serializer_class = serializers.StudentSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def retrieve(self,request,*args,**kwargs):
        if not request.user.is_student:
            return Response({"Error":"User is not an student"},status=403)
        
        if request.user.id != kwargs["pk"]:
            return Response({"Error":"Access Denied"},status=400)

        student = self.queryset.get(user_id=self.kwargs['pk'])
        serializer = self.serializer_class(student)
        return Response(serializer.data)

    def partial_update(self,request,*args,**kwargs):

        if not request.user.is_student:
            return Response({"Error":"User is not an student"},status=403)
        
        if request.user.id != kwargs["pk"]:
            return Response({"Error":"Access Denied"},status=400)

        student = self.queryset.get(user_id=self.kwargs['pk'])
        if 'exam_preparing_for' in request.data:
            if request.data['source'] == 'flutter':
                request.data['exam_preparing_for'] =  ast.literal_eval(request.data['exam_preparing_for'])
                request.data['exam_preparing_for'] = request.data['exam_preparing_for'][0]
            elif request.data['source'] == 'web':
                request.data['exam_preparing_for'] =  ast.literal_eval(request.data['exam_preparing_for']) 
        serializer = self.serializer_class(student,data=request.data,partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=200)
# class StudentViewAPI(RetrieveUpdateAPIView):

#     queryset = models.Student.objects.all()
#     serializer_class = serializers.StudentSerializer
#     permission_classes = [permissions.IsAuthenticated, ]

#     def retrieve(self,request,*args,**kwargs):
#         student = self.queryset.get(user = request.user)
#         serializer = self.serializer_class(student)
#         return Response(serializer.data)
    
#     def partial_update(self,request,*args,**kwargs):
#         student = self.queryset.get(user = request.user)
#         serializer = self.serializer_class(student)
#         #request.data['exam_preparing_for'] =  ast.literal_eval(request.data['exam_preparing_for'])
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         # headers = self.get_success_headers(serializer.data)
#         return Response(serializer.data, status=200)
class StudentSubDetailAPI(ListAPIView):

    queryset = models.PurchasedSubscription.objects.all()
    serializer_class = serializers.PurchasedSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def get_queryset(self):
        queryset = self.queryset.filter(student_id=self.kwargs['pk'])

        queryset =queryset.order_by('date')
        return queryset

class StudentActiveSubDetailAPI(ListAPIView,CreateAPIView):

    queryset = models.PurchasedSubscription.objects.all()
    serializer_class = serializers.PurchasedSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def get_queryset(self):
        queryset = self.queryset.filter(student_id=self.kwargs['pk'],active=True)

        queryset =queryset.order_by('date')

        return queryset

    def create(self,request,*args,**kwargs):
        if request.user.is_student:
            return Response({"error":"Not Allowed"},status=400)

        try:
            student = models.Student.objects.get(id=kwargs["pk"])
        except ObjectDoesNotExist:
            return Response({"error":"Student doesnt exist"},status=400)

        if student.active_subscription is not None:
            return Response({"error":"User already has active subscription"},status=400)

        serializer = serializers.PurchasedSubscriptionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        newSub=serializer.save()       

        serializer = serializers.StudentSerializer(student,data={"active_subscription":newSub.id},partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,status=200)

class TodayDuefeeAPI(ListAPIView):

    queryset = models.Student.objects.all()
    serializer_class = serializers.FollowupDueSerializer
    permission_classes = [permissions.IsAuthenticated, ]

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
        
        queryset = self.queryset.filter(active_subscription__due_date = datetime.date.today(),library_branch=self.kwargs["id"])

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
            queryset = queryset.filter(Q(name__icontains  =search)|Q(id__icontains  =search))

        queryset = queryset.order_by('id')

        serializer = self.serializer_class(queryset,many=True)

        return Response(serializer.data)

class TodayDueCountAPI(APIView):

    queryset = models.Student.objects.all()
    permission_classes = [permissions.IsAuthenticated, ]

    def get(self,request):

        if not request.user.is_owner and not request.user.is_employee:
            return Response({"error":"User is not an owner/employee"},status=401)
        
        if request.user.is_owner:
            instance = models.Owner.objects.get(user = request.user)
        elif request.user.is_employee:
            instance = models.Employee.objects.get(user = request.user)
        
        branchlist = instance.branches.all()
        if int(kwargs["id"]) not in branchlist.values_list('id', flat=True):
            return Response({"Error":"Branch does not belong to this owner/employee"},status=403)

        queryset = self.queryset.filter(active_subscription__due_date = datetime.date.today(),library_branch=self.kwargs["id"])

        return Response({"count":queryset.count()},status=200)
class TodayDuefeeClearApi(RetrieveAPIView):

    queryset = models.PurchasedSubscription.objects.all()
    serializer_class = serializers.PurchasedSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def retrieve(self,request,*args,**kwargs):

        if not request.user.is_owner and not request.user.is_employee:
            return Response({"error":"User is not an owner/employee"},status=401)
        
        if request.user.is_owner:
            instance = models.Owner.objects.get(user = request.user)
        elif request.user.is_employee:
            instance = models.Employee.objects.get(user = request.user)
        
        branchlist = instance.branches.all()
        if int(kwargs["id"]) not in branchlist.values_list('id', flat=True):
            return Response({"Error":"Branch does not belong to this owner/employee"},status=403) 

        try:
            sub = self.queryset.get(student_id=kwargs['pk'],active=True)
        except:
            return Response({"error":"Internal Error"},status=400)
        serializer = self.serializer_class(sub)
        return Response(serializer.data)

class TrackStudentOfftimeTodayAPI(ListAPIView):

    queryset = models.StudentOfftime.objects.all()
    serializer_class = serializers.StudentOfftimeSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def list(self,request,*args,**kiwargs):

        if not request.user.is_owner and not request.user.is_employee:
            return Response({"error":"User is not an owner/employee"},status=401)
        
        if request.user.is_owner:
            instance = models.Owner.objects.get(user = request.user)
        elif request.user.is_employee:
            instance = models.Employee.objects.get(user = request.user)
        
        branchlist = instance.branches.all()
        if int(kwargs["id"]) not in branchlist.values_list('id', flat=True):
            return Response({"Error":"Branch does not belong to this owner/employee"},status=403) 
        
        queryset = self.queryset.filter(date = datetime.date.today(),student__library_branch=self.kwargs["id"])
        
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
            queryset = queryset.filter(Q(student_name__icontains  =search)|Q(student_id__icontains  =search))
        
        queryset = queryset.order_by('id')
        
        serializer = self.get_serializer(queryset,many=True)

        return Response(serializer.data,status=200)

class TrackStudentofftimeTodayCountAPI(APIView):
    queryset = models.StudentOfftime.objects.all()
    permission_classes = [permissions.IsAuthenticated, ]

    def get(self,request):
        
        if not request.user.is_owner and not request.user.is_employee:
            return Response({"error":"User is not an owner/employee"},status=401)
        
        if request.user.is_owner:
            instance = models.Owner.objects.get(user = request.user)
        elif request.user.is_employee:
            instance = models.Employee.objects.get(user = request.user)
        
        branchlist = instance.branches.all()
        if int(kwargs["id"]) not in branchlist.values_list('id', flat=True):
            return Response({"Error":"Branch does not belong to this owner/employee"},status=403) 

        queryset = self.queryset.filter(date = datetime.date.today(),student__library_branch=self.kwargs["id"])

        return Response({"count":queryset.count()},status=200)    
class TrackStudentOfftimeListAPI(ListAPIView,UpdateAPIView):
    
    queryset = models.PurchasedSubscription.objects.all()
    serializer_class = serializers.TrackTotalOfftimeSerailzier
    permission_classes = [permissions.IsAuthenticated, ]

    def get_queryset(self):
        
        queryset = self.queryset.filter(student__library_branch=self.kwargs["id"],active=True)

        search = self.request.query_params.get('search', None)
        if search is not None:
            queryset = queryset.filter(Q(name__icontains  =search)|Q(id__icontains  =search))

        queryset = queryset.order_by('id')
        return queryset

    def partial_update(self,request,*args,**kwargs):

        if not request.user.is_owner and not request.user.is_employee:
            return Response({"error":"User is not an owner/employee"},status=401)
        
        if request.user.is_owner:
            instance = models.Owner.objects.get(user = request.user)
        elif request.user.is_employee:
            instance = models.Employee.objects.get(user = request.user)
        
        branchlist = instance.branches.all()
        if int(kwargs["id"]) not in branchlist.values_list('id', flat=True):
            return Response({"Error":"Branch does not belong to this owner/employee"},status=403) 

        instance = self.queryset.get(id=kwargs["pk"])

        if "totalRollBack" in request.data:
            rollback = datetime.datetime.strptime(request.data["totalRollBack"],"%H:%M:%S").time()
            rollback = datetime.timedelta(hours=(rollback.hour), minutes=(rollback.minute ))
            
            #if instance.totalOffTime.hour - rollback.hour >= 0 and instance.totalOffTime.minute - rollback.minute>=0:
            if instance.totalOffTime - rollback >= datetime.timedelta(0):
                pass
            else:
                return Response({"error":"Roll back time can exceed total off time"},status=400)
            data={
                "totalRollBack":rollback + instance.totalRollBack,
            }
        serializer = self.serializer_class(instance,data=data,partial = True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data,status=200)
class SingleStudentOfftime(ListAPIView):

    queryset = models.StudentOfftime.objects.all()
    serializer_class = serializers.offTimeSerializer
    permission_classes = [permissions.IsAuthenticated, ]

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

        offtimes = models.StudentOfftime.objects.filter(activeSub = kwargs["pk"])

        serializer = self.serializer_class(offtimes,many=True)
        return Response(serializer.data)

class StudentAttendanceStatus(RetrieveAPIView):

    queryset = models.Student.objects.all()
    serializer_class = serializers.StudentMonthlyAttendance
    permission_classes = [permissions.IsAuthenticated, ]

    def retrieve(self,request,*args,**kwargs):

        if not request.user.is_student:
            return Response({"error":"User is not a student"},status=403)

        try:
            student = self.queryset.get(user=self.request.user)
        except ObjectDoesNotExist:
            return Response({"error":"Student does not exist"},status=400)

        serializer = self.serializer_class(student)
        return Response(serializer.data)

class StudentCard(RetrieveAPIView):

    queryset = models.Student.objects.all()
    serializer_class = serializers.StudentCard
    permission_classes = [permissions.IsAuthenticated, ]

    def retrieve(self,request,*args,**kwargs):

        if not request.user.is_student:
            return Response({"error":"User is not a student"},status=403)

        try:
            student = self.queryset.get(user=self.request.user)
        except ObjectDoesNotExist:
            return Response({"error":"Student does not exist"},status=400)

        serializer = self.serializer_class(student)
        return Response(serializer.data,status=200)

# class StudentAttendanceAPI(RetrieveAPIView):

#     queryset = models.Student.objects.all()
#     serializer_class = serializers.StudentYearlyAttendance
#     permission_classes = [permissions.IsAuthenticated, ]

#     def retrieve(self,request,*args,**kwargs):

#         student = self.queryset.get(user=self.request.user)
#         serializer = self.serializer_class(student)
#         return Response(serializer.data)

class StudentAttendanceAPI(APIView):

    queryset = models.Student.objects.all()
    serializer_class = serializers.StudentYearlyAttendance
    permission_classes = [permissions.IsAuthenticated, ]

    def get(self,request):

        if not request.user.is_student:
            return Response({"error":"User is not a student"},status=403)

        try:
            student = self.queryset.get(user=self.request.user)
        except ObjectDoesNotExist:
            return Response({"error":"Student does not exist"},status=400)

        today = datetime.date.today()
        year = self.request.query_params.get('year', None)
        info =[]
        if year is not None:
            
            if int(year) == today.year:
                months= today.month
                year = today.year
            else:
                months=12
                year=int(year)
        else:
            months= today.month
            year = today.year
        for i in range(1,months+1):
            monthStart = today.replace(day=1,month=i)

            counter=1
            present = models.StudentAttendance.objects.filter(student = student, date__month = monthStart.month,date__year=year,present=True)
            presentdays=[]
            for z in present:
                if z.date not in presentdays:
                    presentdays.append(z.date)
            absent = models.StudentAttendance.objects.filter(student = student, date__month = monthStart.month,date__year=year,present=False)
            absentdays=[]
            for z in absent:
                if z.date not in absentdays:
                    absentdays.append(z.date)

            holiday = librarymodels.Holidays.objects.filter(library_branch=student.library_branch,start__month = monthStart.month,start__year=year,active=True)
            holidaydays=[]
            for z in holiday:
                if z.date not in holidaydays:
                    holidaydays.append(z.date)
            data={
                "month":i,
                "present":len(presentdays),
                "presentdays":presentdays,
                "holiday":len(holidaydays),
                "holidaydays":holidaydays,
                "absent": len(absentdays),
                "absentdays":absentdays
            }
            info.append(data)
        return Response(info,status=200)
class StudentOfftimeAPI(ListAPIView):

    queryset = models.StudentOfftime.objects.all()
    serializer_class = serializers.StudentOfftimeSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def list(self,request,*args,**kwargs):
        if not request.user.is_student:
            return Response({"error":"User is not a student"},status=403)

        try:
            student = models.Student.objects.get(user=self.request.user)
        except ObjectDoesNotExist:
            return Response({"error":"Student does not exist"},status=400)

        if student.active_subscription is None:
            sub = models.PurchasedSubscription.objects.filter(student=student)[0]
        else:
            sub = models.PurchasedSubscription.objects.get(id=student.active_subscription)
        
        offtimeObj = self.queryset.filter(activeSub=sub)

        serializer = self.serializer_class(offtimeObj,many=True)
        return Response(serializer.data)

class OwnerStudentAttendanceAPI(ListAPIView):
    queryset = models.StudentAttendance.objects.all()
    serializer_class = serializers.OwnerStudentAttendanceSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    # def retrieve(self,request,*args,**kwargs):
    #     today = datetime.date.today()

    #     data=[]

    #     try:
    #         owner = ownermodels.Owner.objects.get(user=request.user)
    #     except ObjectDoesNotExist:
    #         return Response({"error":"User is not an owner"},status=400)

    #     branch = self.request.query_params.get('branch', None)
    #     if branch is not None:
    #         if branch == 'all':
    #             queryset = self.queryset.filter(branch__in=owner.branches)
    #             #queryset = self.queryset.filter(library_branch__library=owner.library).order_by("-id")
    #         else:
    #             queryset = self.queryset.filter(branch=int(branch))   
    #     else:
    #         return Response({"error":"Brach ?branch is required"},status=400)

    #     time = self.request.query_params.get('time', None)
    #     if time is not None:
    #         time = datetime.datetime.strptime(time, '%H:%M:%S')
    #         queryset = queryset.filter(branch=kwargs["id"],slot__start__lte=time,slot__end__gte=time,date=today)

    #     present = self.request.query_params.get('present', None)
    #     if present is not None:
    #         queryset = queryset.filter(branch=kwargs["id"],present=True,date=today)
        
    #     absent = self.request.query_params.get('absent', None)
    #     if absent is not None:
    #         queryset = queryset.filter(branch=kwargs["id"],present=False,date=today)
        
    #     from_date = self.request.query_params.get('from_Date', None)
    #     if from_date is not None:
    #         from_date = datetime.datetime.strptime(from_date, "%Y-%m-%d").date()
    #         queryset = queryset.filter(branch=kwargs["id"],date__gte = from_date)

    #     to_date = self.request.query_params.get('to_date', None)
    #     if to_date is not None:
    #         to_date = datetime.datetime.strptime(to_date, "%Y-%m-%d").date()
    #         queryset = queryset.filter(branch=kwargs["id"],date__lte = to_date)
    #     search = self.request.query_params.get('search', None)
    #     if search is not None:
    #         queryset = queryset.filter(Q(student__name__icontains=search)|Q(student__id__icontains=search))
    #     data=[]
    #     if branch == "all":
    #         for i in owner.branches.all():
    #             temp=queryset.filter(library_branch=i)
    #             serializer = self.get_serializer(temp,many=True)
    #             data.append({
    #                 "branch name":i.name,
    #                 "branch id":i.id,
    #                 "expense":serializer.data
    #             })
    #     else:
    #         temp=queryset.filter(library_branch=int(branch))
    #         serializer = self.get_serializer(temp,many=True)
    #         data.append({
    #             "branch name":i.name,
    #             "branch id":i.id,
    #             "expense":serializer.data
    #         })
    def list(self,request,*args,**kwargs):
        today = datetime.date.today()
        print(today)
        queryset = self.queryset.filter(branch=kwargs["id"])
        #now = datetime.datetime.now().time()
        time = self.request.query_params.get('time', None)
        if time is not None:
            time = datetime.datetime.strptime(time, '%H:%M:%S')
            queryset = queryset.filter(branch=kwargs["id"],slot__start__lte=time,slot__end__gte=time,date=today)

        present = self.request.query_params.get('present', None)
        if present is not None:
            queryset = queryset.filter(branch=kwargs["id"],present=True,date=today)
        
        absent = self.request.query_params.get('absent', None)
        if absent is not None:
            queryset = queryset.filter(branch=kwargs["id"],present=False,date=today)
        
        from_date = self.request.query_params.get('from_Date', None)
        if from_date is not None:
            from_date = datetime.datetime.strptime(from_date, "%Y-%m-%d").date()
            queryset = queryset.filter(branch=kwargs["id"],date__gte = from_date)

        to_date = self.request.query_params.get('to_date', None)
        if to_date is not None:
            to_date = datetime.datetime.strptime(to_date, "%Y-%m-%d").date()
            queryset = queryset.filter(branch=kwargs["id"],date__lte = to_date)
        #student = self.queryset.filter(library_branch=kwargs["id"],active_subscription__timeslots__in=coremodels.TimeSlot.objects.filter(start__lte=now,end__gte=now))
        #attendance = self.queryset.filter
        search = self.request.query_params.get('search', None)
        if search is not None:
            queryset = queryset.filter(Q(student__name__icontains=search)|Q(student__id__icontains=search))

        serializer = self.serializer_class(queryset,many=True)
        return Response(serializer.data)

class OwnerStudentAttendanceUpdateAPI(UpdateAPIView):
    queryset = models.StudentAttendance.objects.all()
    serializer_class = serializers.StudentAttendanceSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def partial_update(self,request,*args,**kwargs):

        OpenObj = self.queryset.get(id=kwargs["pk"])

        studentObj = models.Student.objects.get(id=OpenObj.student.id)

        instances = self.queryset.filter(branch=OpenObj.branch,student=OpenObj.student,out_time__isnull=True)
        if not instances:

            return Response({"error":"No Attendance Open For Closing Please Check Or Report To Owner"},status=409)
        currentSlot=coremodels.TimeSlot.objects.get(id=OpenObj.slot.id)

        endtime = datetime.datetime.strptime(request.data["out_time"],"%H:%M:%S").time()

        offtime = datetime.timedelta(0)

        if endtime >currentSlot.end:
            offtime = datetime.timedelta(hours=(endtime.hour - currentSlot.end.hour), minutes=(endtime.minute - currentSlot.end.minute))

        if currentSlot.start>endtime:
            obj, created = models.StudentOfftime.objects.get_or_create(student=studentObj,slot=currentSlot.id,activeSub=studentObj.active_subscription,date=datetime.datetime.strptime(request.data["date"], '%Y-%m-%d').date())

            activeSub = models.PurchasedSubscription.objects.get(id=studentObj.active_subscription.id)
            offtime = datetime.timedelta(hours=(currentSlot.start.hour - endtime.hour), minutes=(currentSlot.start.minute-endtime.minute))

            obj.offtime = obj.offtime - offtime
            activeSub.totalOffTime = activeSub.totalOffTime - offtime
            activeSub.save()
            obj.slot=None
            obj.save()
            offtime = datetime.timedelta(0)
            request.data["slot"]=None
        else:
            pass

        if offtime == datetime.timedelta(0):
            pass
        else:
            obj, created = models.StudentOfftime.objects.get_or_create(student=studentObj,slot=currentSlot.id,activeSub=studentObj.active_subscription,date=datetime.datetime.strptime(request.data["date"], '%Y-%m-%d').date())

            activeSub = models.PurchasedSubscription.objects.get(id=studentObj.active_subscription.id)
            if created:
                obj.offtime = offtime
                obj.save()
            else:
                obj.offtime = offtime + obj.offtime
                obj.save()
            activeSub.totalOffTime = activeSub.totalOffTime + offtime
            temp = models.StudentAttendance.objects.filter(student=studentObj,slot=currentSlot.id,date=datetime.datetime.strptime(request.data["date"], '%Y-%m-%d').date())

            if temp.count()>1:
                pass
            else:
                activeSub.hoursUtilized = activeSub.hoursUtilized + (datetime.timedelta(hours=(currentSlot.end.hour - currentSlot.start.hour), minutes=(currentSlot.end.minute - currentSlot.start.minute)))
            activeSub.save()
        serializer = self.get_serializer(OpenObj,data=request.data,partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        #headers = self.get_success_headers(serializer.data)
        return Response("Attendance Updated Successfully", status=200)
class StudentAttendanceOfftimeCheckAPI(CreateAPIView):
    queryset = models.StudentAttendance.objects.all()
    serializer_class = serializers.StudentAttendanceSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def create(self,request,*args,**kwargs):
        if not request.user.is_student:
            return Response({"error":"User is not a student"},status=403)

        studentObj = models.Student.objects.get(user=request.user)

        try:
            qrObj = librarymodels.AttendanceQrCode.objects.get(branch=studentObj.library_branch,qrcode=request.data["qrcode"],active=True)
        except ObjectDoesNotExist:
            return Response({"error":"Attendance Qr Code is invalid "},status= 403)
        instances = self.queryset.filter(branch=studentObj.library_branch,student=studentObj,out_time__isnull=True,present=True)
        if instances:
            return Response({"error":"Previous Attendance Not Closed Please Check Or Report To Owner"},status=409)

        if studentObj.active_subscription is None:
            return Response({"error":"No Active Subscription On Going Please Check"},status=400)
        
        currentSlot=studentObj.active_subscription.timeslots.all()[0]
        intime = datetime.datetime.strptime(request.data["in_time"],"%H:%M:%S").time()
        for slot in studentObj.active_subscription.timeslots.all().order_by('start'):

            if intime >= slot.start and intime <= slot.end:
                currentSlot=slot
                break
            elif intime  <= slot.start and currentSlot.start<=slot.start:
                currentSlot=slot
                break
        if slot.end < intime:
            return Response({"warning":"Next slot is tomorrow"},status=200)

        offtime = datetime.timedelta(0)
        if intime <currentSlot.start:
            offtime = datetime.timedelta(hours=(currentSlot.start.hour - intime.hour), minutes=(currentSlot.start.minute - intime.minute)) 
        
        currentslottime = datetime.timedelta(hours=(currentSlot.end.hour - currentSlot.start.hour), minutes=(currentSlot.end.minute - currentSlot.start.minute)) 

        if currentslottime > studentObj.active_subscription.hoursRemain:
            extratime = datetime.timedelta(minutes=30)
            if offtime == datetime.timedelta(0):
                if currentslottime <= studentObj.active_subscription.hoursRemain+extratime:
                    return Response({"warning":"Subscription Final hours","remaining":studentObj.active_subscription.hoursRemain+extratime},status=200)
                else:
                    return Response({"error":"Insufficent hours remaining"},status=400)
            else:
                return Response({"error":"Insufficent hours remaining please try to enter during slot hours"},status=400)
        
        return Response({"offtime":str(offtime)},status=200)


class NotificationCentreAPI(ListAPIView,DestroyAPIView):

    queryset = models.Student.objects.all()
    serializer_class = coreserializers.StudentNotificationSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def list(self,request,*args,**kwargs):
        if not request.user.is_student:
            return Response({"error":"Access Denied"},status=403)
        try:
            student = self.queryset.get(user=self.request.user)
        except ObjectDoesNotExist:
            return Response({"Error":"User is not a student"},status=400)

        notifications = coremodels.Notifications.objects.filter(student=student).order_by("-id")

        serializer = self.serializer_class(notifications,many=True)

        return Response(serializer.data)

    def delete(self,request,*args,**kwargs):
        if not request.user.is_student:
            return Response({"error":"Access Denied"},status=403)
        try:
            student = self.queryset.get(user=self.request.user)
        except ObjectDoesNotExist:
            return Response({"Error":"User is not a student please check"},status=400)

        instance = coremodels.Notifications.objects.get(id=kwargs["id"])

        instance.delete()
        return Response("Deleted Successfully",status=200)


class StudentManagePendingsAPI(ListAPIView):
    queryset = models.PurchasedSubscription.objects.all()
    serializer_class = serializers.StudentManageSubSerializer
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

class NewAdmissionListAPI(APIView):
    queryset = models.Student.objects.all()
    permission_classes = [permissions.IsAuthenticated, ]

    def get(self,request,id):
        today = datetime.date.today()
        queryset = self.queryset.filter(library_branch=self.kwargs["id"]).order_by("-id")
        data=[]
        from_date = self.request.query_params.get('from_Date', None)

        for student in queryset:
            sub = models.PurchasedSubscription.objects.filter(student=student)
            from_date = self.request.query_params.get('from_date', None)
            if from_date is not None:
                from_date = datetime.datetime.strptime(from_date, "%Y-%m-%d").date()
                sub = sub.filter(date__gte = from_date)

            to_date = self.request.query_params.get('to_date', None)
            if to_date is not None:
                to_date = datetime.datetime.strptime(to_date, "%Y-%m-%d").date()
                sub = sub.filter(date__lte = to_date)
            # past = self.request.query_params.get('past', None)
            # if past is not None:
            #     if past=="days":
            #         days = 10
            #         if today.day <10:

            if sub.count()>0:
                sub = sub.order_by("id")
                timeslots = sub[0].timeslots.all()
                serializer = coreserializers.TimeSlotSerializer(timeslots,many=True)
                
                try:
                    image=student.image.url
                except:
                    image=""
                data.append(
                    {
                        "id":student.id,
                        "name":student.name,
                        "image":image,
                        "timeslot":serializer.data
                    })
        return Response(data,status=200)

class StudentRenewalListAPI(APIView):
    queryset = models.Student.objects.all()
    permission_classes = [permissions.IsAuthenticated, ]

    def get(self,request,id):
        today = datetime.date.today()
        queryset = self.queryset.filter(library_branch=self.kwargs["id"]).order_by("-id")
        data=[]
        from_date = self.request.query_params.get('from_Date', None)

        for student in queryset:
            sub = models.PurchasedSubscription.objects.filter(student=student)
            from_date = self.request.query_params.get('from_date', None)
            if from_date is not None:
                from_date = datetime.datetime.strptime(from_date, "%Y-%m-%d").date()
                sub = sub.filter(date__gte = from_date)

            to_date = self.request.query_params.get('to_date', None)
            if to_date is not None:
                to_date = datetime.datetime.strptime(to_date, "%Y-%m-%d").date()
                sub = sub.filter(date__lte = to_date)
            # past = self.request.query_params.get('past', None)
            # if past is not None:
            #     if past=="days":
            #         days = 10
            #         if today.day <10:

            if sub.count()>1:
                sub = sub.order_by("id")
                timeslots = sub[0].timeslots.all()
                serializer = coreserializers.TimeSlotSerializer(timeslots,many=True)
                
                try:
                    image=student.image.url
                except:
                    image=""
                data.append(
                    {
                        "id":student.id,
                        "name":student.name,
                        "image":image,
                        "timeslot":serializer.data
                    })
        return Response(data,status=200)

class NewAdmissionCSVAPI(APIView):
    queryset = models.Student.objects.all()
    permission_classes = [permissions.IsAuthenticated, ]

    def get(self,request,id):
        today = datetime.date.today()
        queryset = self.queryset.filter(library_branch=self.kwargs["id"]).order_by("-id")
        data=[]
        from_date = self.request.query_params.get('from_Date', None)

        for student in queryset:
            sub = models.PurchasedSubscription.objects.filter(student=student)
            from_date = self.request.query_params.get('from_date', None)
            if from_date is not None:
                from_date = datetime.datetime.strptime(from_date, "%Y-%m-%d").date()
                sub = sub.filter(date__gte = from_date)

            to_date = self.request.query_params.get('to_date', None)
            if to_date is not None:
                to_date = datetime.datetime.strptime(to_date, "%Y-%m-%d").date()
                sub = sub.filter(date__lte = to_date)
            
            if sub.count()>0:
                slots=[]
                sub = sub.order_by("id")
                timeslots = sub[0].timeslots.all()
                for slot in timeslots:
                    slots.append({
                        "start":str(slot.start),
                        "end":str(slot.end)
                    })              
                try:
                    image=student.image.url
                except:
                    image=""
                data.append(
                    {
                        "id":student.id,
                        "name":student.name,
                        "timeslot":slots
                    })
        response = HttpResponse(content_type='text/csv')  
        response['Content-Disposition'] = 'attachment; filename="file.csv"'  
        writer = csv.DictWriter(response,fieldnames=keys)
        writer.writeheader()
        for i in data:  
            writer.writerow(i)  
        return response

class NewAdmissionCSVMailAPI(APIView):
    queryset = models.Student.objects.all()
    permission_classes = [permissions.IsAuthenticated, ]

    def get(self,request,id):
        today = datetime.date.today()
        queryset = self.queryset.filter(library_branch=self.kwargs["id"]).order_by("-id")
        data=[]
        from_date = self.request.query_params.get('from_Date', None)

        for student in queryset:
            sub = models.PurchasedSubscription.objects.filter(student=student)
            from_date = self.request.query_params.get('from_date', None)
            if from_date is not None:
                from_date = datetime.datetime.strptime(from_date, "%Y-%m-%d").date()
                sub = sub.filter(date__gte = from_date)

            to_date = self.request.query_params.get('to_date', None)
            if to_date is not None:
                to_date = datetime.datetime.strptime(to_date, "%Y-%m-%d").date()
                sub = sub.filter(date__lte = to_date)
            
            if sub.count()>0:
                slots=[]
                sub = sub.order_by("id")
                timeslots = sub[0].timeslots.all()
                for slot in timeslots:
                    slots.append({
                        "start":str(slot.start),
                        "end":str(slot.end)
                    })              
                try:
                    image=student.image.url
                except:
                    image=""
                data.append(
                    {
                        "id":student.id,
                        "name":student.name,
                        "timeslot":slots
                    })
        csvfile = StringIO()
        fieldnames = list(data[0].keys())
        writer = csv.DictWriter(csvfile,fieldnames=fieldnames)
        writer.writeheader()
        for i in data:  
            writer.writerow(i)  
        email = EmailMessage(
        subject='Subject',
        body='Body',
        from_email='testingserver.12307@gmail.com',
        to=['yashch1998@gmail.com'],
        )
        email.attach('file.csv', csvfile.getvalue(), 'text/csv')
        email.send()
        return Response("Email Sent Successfully",status=200)

class StudentLibraryOfferAPI(ListAPIView):
    queryset = librarymodels.LibraryOffer.objects.all()
    serializer_class = libraryserializers.LibraryOfferSerializer
    permission_class = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        if not request.user.is_student:
            return Response({"Error":"User is not a student"},status=401)

        student = models.Student.objects.get(user=request.user)

        queryset = self.queryset.filter(library=student.library_branch)

        serializer = self.get_serializer(queryset,many=True)

        return Response(serializer.data,status=200)