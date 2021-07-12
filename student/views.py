from django.shortcuts import render
from . import models, serializers
from rest_framework import viewsets, status, permissions
import datetime
from rest_framework.decorators import action
from django.db.models import Q
from rest_framework.response import Response
from core import models as coremodels
from library import models as librarymodels
from owner import models as ownermodels
from django.core.exceptions import ObjectDoesNotExist
import ast
from rest_framework.generics import *
from django.db import IntegrityError

import uuid
from pyfcm import FCMNotification
from django.conf import settings

class StudentAPIViewSet(viewsets.ModelViewSet):
    queryset = models.Student.objects.all()
    serializer_class = serializers.StudentSerializer
    permission_classes = [permissions.IsAuthenticated, ]
    http_method_names = ['post','update','options','head']

    def get_queryset(self):
        queryset = models.Student.objects.all()

        # status = self.request.query_params.get('status', None)
        # if status is not None:
        #     if status == 'inactive':
        #         queryset = queryset.filter(active_subscription__isnull = True)
        #     elif status == 'active':
        #         queryset = queryset.filter(active_subscription__isnull = False)
        active = self.request.query_params.get('active', None)
        if active is not None:
            queryset = queryset.filter(active_subscription__isnull=active)

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
            queryset = queryset.filter(Q(name__icontains  =search)|Q(address__icontains  =search)|Q(city__icontains  =search)|Q(state__icontains  =search)|Q(location__icontains  =search))

        queryset = queryset.order_by('name')
        return queryset

    @action(detail = False)
    def absent_from_7_days(self, request):
        serializer_context = {
            'request': request,
        }
        queryset = self.get_queryset()
        students = []
        for student in queryset:
            attendance = models.StudentAttendance.objects.filter(student=student).order_by('-date')
            dt = datetime.date.today() - datetime.timedelta(7)
            if attendance.exists():
                last_attendance = attendance[0]
                if last_attendance.date < dt:
                    students.append(student)
        data = serializers.StudentSerializer(students, many=True, context=serializer_context).data
        return Response(data)

    @action(detail = False, methods = ['get'], permission_classes=[permissions.IsAuthenticated])
    def new_admissions(self, request):
        serializer_context = {
            'request': request,
        }
        queryset = self.get_queryset()
        days = request.query_params.get('days', None)
        if days is not None:
            days = int(days)
            dt = datetime.date.today() - datetime.timedelta(days)
            queryset = queryset.filter(add_date__gte=dt)
        data = serializers.StudentSerializer(queryset, many=True, context=serializer_context).data
        return Response(data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def renewals(self, request):
        serializer_context = {
            'request': request,
        }
        queryset = self.get_queryset()
        today = datetime.date.today()
        queryset = queryset.filter(add_date__lt=today, active_subscription__date=today)
        data = serializers.StudentSerializer(queryset, many=True, context=serializer_context).data
        return Response(data)

    @action(detail = False, methods = ['get'], permission_classes=[permissions.IsAuthenticated])
    def due_fees(self, request):
        final_students = []
        serializer_context = {
            'request': request,
        }
        queryset = self.get_queryset()

        days = request.query_params.get('days', None)
        if days is not None:
            days = int(days)
            dt = datetime.date.today() + datetime.timedelta(days)
            queryset = queryset.filter(active_subscription__due_date__lte=dt)

        for student in queryset:
            subscriptions = models.PurchasedSubscription.objects.filter(student=student)
            total_amount = subscriptions.aggregate(Sum('total_amount'))
            total_amount = total_amount['Sum']
            payments = models.StudentPayment.objects.filter(purchased_subscription__in=subscriptions).aggregate(
                Sum('amount_paid'))
            payments = payments['Sum']
            due = total_amount - payments
            if due:
                final_students.append(student)
        data = serializers.StudentSerializer(final_students, many=True, context=serializer_context).data
        return Response(data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def renew_subscriptions(self, request):
        final_students = []
        serializer_context = {
            'request': request,
        }
        queryset = self.get_queryset()

        days = request.query_params.get('days', None)
        if days is not None:
            days = int(days)
            dt_upper = datetime.date.today() + datetime.timedelta(days)
            dt_lower = datetime.date.today() - datetime.timedelta(days)

            for student in queryset:
                end_date = student.from_date + datetime.timedelta(days = student.days)
                if dt_lower <= end_date <= dt_upper:
                    final_students.append(student)
        data = serializers.StudentSerializer(final_students, many=True, context=serializer_context).data
        return Response(data)

    @action(detail = False, methods = ['get'], permission_classes=[permissions.IsAuthenticated])
    def live_students(self, request):
        pass


    def create(self, request, *args, **kwargs):
        if request.user.is_student:
            return Response({"error":"Access Denied"},status=403)
        mobile = request.data.get('mobile')
        dob = request.data.get('dob')

        if request.user.is_owner:
            instance = ownermodels.Owner.objects.get(user=request.user)
        elif request.user.is_employee:
            instance = ownermodels.Employee.objects.get(user=request.user)

        branchlist = instance.branches.all()
        if int(request.data["library_branch"]) not in branchlist.values_list('id', flat=True):
            return Response({"Error":"Branch does not belong to this owner/employee"},status=403)

        try:
            user = coremodels.User.objects.create_user(username=mobile, email=request.data["email"],password=mobile,is_student=True)
        except IntegrityError:
            return Response("User already exisiting with same phone number please check",status=400)
        request.data['user'] = user.id
        if request.data['source'] == 'flutter':
            request.data['exam_preparing_for'] =  ast.literal_eval(request.data['exam_preparing_for'])
            request.data['exam_preparing_for'] =  request.data['exam_preparing_for'][0]
        elif request.data['source'] == 'web':
            request.data['exam_preparing_for'] =  ast.literal_eval(request.data['exam_preparing_for'])
        request.data["referral_code"]=str(uuid.uuid4().hex[:7].upper())

        serializer = self.get_serializer(data=request.data)
        #serializer.is_valid(raise_exception=True)
        if not serializer.is_valid():
            user.delete()
            raise ValidationError(serializer.errors)
        else:
            self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class StudentAttendanceAPIViewSet(viewsets.ModelViewSet):
    queryset = models.StudentAttendance.objects.all()
    serializer_class = serializers.StudentAttendanceSerializer
    permission_classes = [permissions.IsAuthenticated, ]
    http_method_names = ['post','update','options','head']

    def create(self,request,*args,**kwargs):
        if not request.user.is_student:
            return Response({"Error":"User is not a student"},status=403)
        
        studentObj = models.Student.objects.get(user=request.user)

        try:
            qrObj = librarymodels.AttendanceQrCode.objects.get(branch=studentObj.library_branch,qrcode=request.data["qrcode"],active=True)
        except ObjectDoesNotExist:
            return Response({"error":"Attendance Qr Code is invalid "},status= 403)

        instances = self.queryset.filter(branch=studentObj.library_branch,student=studentObj,out_time__isnull=True,present=True)
        if instances:
            return Response({"error":"Previous Attendance Not Closed Please Check Or Report To Owner"},status=409)

        if studentObj.active_subscription is None:
            return Response({"error":"No Active Subscription On Going Please Check"})
        
        currentSlot=studentObj.active_subscription.timeslots.all()[0]
        intime = datetime.datetime.strptime(request.data["in_time"],"%H:%M:%S").time()
        for slot in studentObj.active_subscription.timeslots.all().order_by('start'):

            if intime >= slot.start and intime <= slot.end:
                currentSlot=slot
                break
            elif intime  <= slot.start and currentSlot.start<=slot.start:
                currentSlot=slot
                break

        request.data["branch"]=studentObj.library_branch.id
        request.data["student"]=studentObj.id

        offtime = datetime.timedelta(0)
        currentslottime = datetime.timedelta(hours=(currentSlot.end.hour - currentSlot.start.hour), minutes=(currentSlot.end.minute - currentSlot.start.minute))

        if intime <currentSlot.start:
            offtime = datetime.timedelta(hours=(currentSlot.start.hour - intime.hour), minutes=(currentSlot.start.minute - intime.minute)) 
            
        if currentslottime > studentObj.active_subscription.hoursRemain:
            extratime = datetime.timedelta(minutes=30)
            if offtime == datetime.timedelta(0):
                if currentslottime <= studentObj.active_subscription.hoursRemain+extratime:
                    
                    push_service = FCMNotification(api_key=settings.FCM_APIKEY)

                    owners = ownermodels.Owner.objects.filter(branches__in=[studentObj.library_branch])
                    ids=[]

                    for owner in owners:
                        try:
                            device = ownermodels.OwnerDevice.objects.get(owner=owner)
                            ids.append(device.registration_id)
                        except ObjectDoesNotExist:
                            pass

                    message_title = "Final Slot for student "+str(studentObj.name)+" has started"
                    message_body = "Final Slot for student "+str(studentObj.name)+" has started.\n Student id is "+str(studentObj.id)
                    result = push_service.notify_multiple_devices(registration_ids=ids, message_title=message_title, message_body=message_body)
                    print(result)

                else:
                    return Response({"error":"Insufficent hours remaining"},status=400)
            else:
                return Response({"error":"Insufficent hours remaining please try to enter during slot hours"},status=400)

        if offtime == datetime.timedelta(0):
            pass
        else:
            obj, created = models.StudentOfftime.objects.get_or_create(student=studentObj,activeSub=studentObj.active_subscription,slot=currentSlot,date=datetime.datetime.strptime(request.data["date"], '%Y-%m-%d').date())
            activeSub = models.PurchasedSubscription.objects.get(id=studentObj.active_subscription.id)
            if created:
                obj.offtime = offtime
                obj.save()
            else:
                obj.offtime = offtime + obj.offtime
                obj.save()

            activeSub.totalOffTime = activeSub.totalOffTime + offtime
            activeSub.save()
        request.data["slot"]=currentSlot.id
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        attendance = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def partial_update(self,request,*args,**kwargs):
        if not request.user.is_student:
            return Response({"Error":"User is not a student"},status=403)

        OpenObj = self.queryset.get(id=kwargs["pk"])
        try:
            qrObj = librarymodels.AttendanceQrCode.objects.get(branch=OpenObj.branch,qrcode=request.data["qrcode"],active=True)
        except ObjectDoesNotExist:
            return Response({"error":"Attendance Qr Code is invalid "},status= 403)

        instances = self.queryset.filter(branch=OpenObj.branch,student=OpenObj.student,out_time__isnull=True)
        if not instances:

            return Response({"error":"No Attendance Open For Closing Please Check Or Report To Owner"},status=409)
        studentObj = models.Student.objects.get(id=OpenObj.student_id)

        if studentObj.active_subscription is None:
            return Response({"error":"No Active Subscription On Going Please Check"})

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
            obj, created = models.StudentOfftime.objects.get_or_create(student=studentObj,slot=currentSlot,activeSub=studentObj.active_subscription,date=datetime.datetime.strptime(request.data["date"], '%Y-%m-%d').date())

            activeSub = models.PurchasedSubscription.objects.get(id=studentObj.active_subscription.id)
            if created:
                obj.offtime = offtime
                obj.save()
            else:
                obj.offtime = offtime + obj.offtime
                obj.save()
            activeSub.totalOffTime = activeSub.totalOffTime + offtime
            temp = models.StudentAttendance.objects.filter(student=studentObj,slot=currentSlot,date=datetime.datetime.strptime(request.data["date"], '%Y-%m-%d').date())

            if temp.count()>1:
                pass
            else:
                activeSub.hoursUtilized = activeSub.hoursUtilized + (datetime.timedelta(hours=(currentSlot.end.hour - currentSlot.start.hour), minutes=(currentSlot.end.minute - currentSlot.start.minute)))
            activeSub.save()
        serializer = self.get_serializer(OpenObj,data=request.data,partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        #headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=200)

class PurchasedSubscriptionAPIViewSet(viewsets.ModelViewSet):
    queryset = models.PurchasedSubscription.objects.all()
    serializer_class = serializers.PurchasedSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated, ]
    http_method_names = ['post','update','options','head']

    def create(self, request, *args, **kwargs):
        if request.user.is_student:
            return Response({"Error":"User is not a Owner/Employee"},status=403)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        if 'payment_mode' in request.data:
            payment_mode = request.data['payment_mode']
            amount_paid = request.data['amount_paid']
            payment = models.StudentPayment.objects.create(payment_mode=payment_mode, amount_paid=amount_paid, purchased_subscription_id =serializer.data['id'])
            payment.save()
        student = models.Student.objects.get(id=request.data["student"])
        sub = self.queryset.get(id=serializer.data["id"])
        student.active_subscription=sub
        student.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class StudentPaymentAPIViewSet(viewsets.ModelViewSet):
    queryset = models.StudentPayment.objects.all()
    serializer_class = serializers.StudentPaymentSerializer
    permission_classes = [permissions.IsAuthenticated, ]
    http_method_names = ['post', 'head','options']

    # def get_queryset(self):
    #     queryset = models.Student.objects.all()
    #
    #     subcategory = self.request.query_params.get('subcategory', None)
    #     if subcategory is not None:
    #         queryset = queryset.filter(sub_category__name__iexact=subcategory)
    #
    #     price = self.request.query_params.get('price', None)
    #     if price is not None:
    #         queryset = queryset.filter(price__exact=int(price))
    #
    #     search = self.request.query_params.get('search', None)
    #     if search is not None:
    #         queryset = queryset.filter(name__icontains=search)
    #     return queryset
    #
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
    #
    # def get_permissions(self):
    #     if self.action == 'list':
    #         permission_classes = [IsAuthenticated]
    #     else:
    #         permission_classes = [IsAdminUser]
    #     return [permission() for permission in permission_classes]
    #
    #
    # @action(detail=True, methods=['post'], permission_classes=[IsAdminOrIsSelf])
    # def set_password(self, request, pk=None):






