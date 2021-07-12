from rest_framework import serializers
from library.models import *
from . import models
from django.contrib.auth.models import User
from django.db.models import Sum
import datetime
from django.core.exceptions import *
from calendar import monthrange
from library import models as librarymodels
from core import serializers as coreserializers
import calendar
from django.db.models import Q
class StudentMinSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Student
        fields = ["id","name","image","verified","active_subscription"]
class StudentSerializer(serializers.ModelSerializer):
    subscriptions = serializers.SerializerMethodField(read_only=True)
    due_fees = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.Student
        fields = "__all__"

    def get_subscriptions(self, obj):
        subscriptions = models.PurchasedSubscription.objects.filter(student=obj).order_by('-date')
        serializer = PurchasedSubscriptionSerializer(subscriptions, many=True)
        return serializer.data

    def get_due_fees(self, obj):
        subscriptions = models.PurchasedSubscription.objects.filter(student=obj)
        total_amount = subscriptions.aggregate(Sum('total_amount'))
        total_amount = total_amount['total_amount__sum']
        if total_amount:
            payments = models.StudentPayment.objects.filter(purchased_subscription__in=subscriptions).aggregate(Sum('amount_paid'))
            payments = payments['amount_paid__sum']
            if payments:
                due = total_amount - payments
                return int(due)
            else:
                return total_amount
        else:
            return None

class StudentAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.StudentAttendance
        fields = "__all__"


class PurchasedSubscriptionSerializer(serializers.ModelSerializer):
    payments = serializers.SerializerMethodField(read_only=True)
    due_days = serializers.SerializerMethodField(read_only=True)
    due_fees = serializers.SerializerMethodField(read_only=True)
    renewals = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = models.PurchasedSubscription
        fields = "__all__"

    def get_payments(self, obj):
        payments = models.StudentPayment.objects.filter(purchased_subscription = obj)
        serializer = StudentPaymentSerializer(payments, many=True)
        return serializer.data

    def get_due_days(self, obj):
        payments = models.StudentPayment.objects.filter(purchased_subscription=obj).aggregate(Sum('amount_paid'))
        payments = payments['amount_paid__sum']
        if payments:
            due = obj.total_amount - payments
            if due <= 0:
                return None
        if obj.due_date:
            today = datetime.date.today()
            days = (obj.due_date - today).days
            return int(days)
        else:
            return 0

    def get_due_fees(self, obj):
        payments = models.StudentPayment.objects.filter(purchased_subscription=obj).aggregate(Sum('amount_paid'))
        payments = payments['amount_paid__sum']
        if payments:
            due = obj.total_amount - payments
            return int(due)
        return obj.total_amount

    def get_renewals(self,obj):
        subs = models.PurchasedSubscription.objects.filter(student_id = obj.student_id)
        return subs.count()

    # def create(self, validated_data):
    #     return models.PurchasedSubscription.objects.create(**validated_data)

class StudentPaymentSerializer(serializers.ModelSerializer):
    # url = serializers.HyperlinkedIdentityField(view_name="studentpayment-detail")

    class Meta:
        model = models.StudentPayment
        fields = "__all__"

class FollowupDueSerializer(serializers.ModelSerializer):

    due_fees = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.Student
        fields = ["id","name","image","verified","active_subscription","due_fees"]


    def get_due_fees(self, obj):
        subscriptions = models.PurchasedSubscription.objects.filter(student=obj)
        total_amount = subscriptions.aggregate(Sum('total_amount'))
        total_amount = total_amount['total_amount__sum']
        if total_amount:
            payments = models.StudentPayment.objects.filter(purchased_subscription__in=subscriptions).aggregate(Sum('amount_paid'))
            payments = payments['amount_paid__sum']
            if payments:
                due = total_amount - payments
                return int(due)
            else:
                return total_amount
        else:
            return None

class StudentInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Student
        fields = ["id","name","verified"]

class StudentOfftimeSerializer(serializers.ModelSerializer):

    studentInfo = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = models.StudentOfftime
        fields = '__all__'

    def get_studentInfo(self,obj):
        student = models.Student.objects.get(id = obj.student_id)
        serializer = StudentInfoSerializer(student)
        return serializer.data
class StudentSubOffTimeSerializer(serializers.ModelSerializer):

    totalOfftime = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = models.Student
        fields = ["id","name","verified","totalOfftime"]

    def get_totalOfftime(self,obj):

        activeSub = models.PurchasedSubscription.objects.get(student=obj,active=True)

        return activeSub.totalOffTime

class StudentMonthlyAttendance(serializers.ModelSerializer):

    dayspresent = serializers.SerializerMethodField(read_only=True)
    datepresent = serializers.SerializerMethodField(read_only=True)
    holidays = serializers.SerializerMethodField(read_only=True)
    dateabsent = serializers.SerializerMethodField(read_only=True)
    daysabsent = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = models.Student
        fields = ["dayspresent","holidays","daysabsent","datepresent","dateabsent"]

    def get_dayspresent(self,obj):
        today = datetime.date.today()
        student = models.StudentAttendance.objects.filter(student = obj.id,date__lte=today, date__month = today.month,date__year=today.year,present=True)
        presentdays=[]
        for z in student:
            if z.date not in presentdays:
                presentdays.append(z.date)
        return len(presentdays)

    def get_datepresent(self,obj):
        today = datetime.date.today()
        student = models.StudentAttendance.objects.filter(student = obj.id,date__lte=today, date__month = today.month,date__year=today.year,present=True)
        date = []
        for i in student:
            if i.date not in date:
                date.append(i.date)
        return date

    def get_holidays(self,obj):
        today = datetime.date.today()
        holiday = librarymodels.Holidays.objects.filter(library_branch=obj.library_branch,start__lte=today,start__month = today.month,start__year=today.year,active=True)
        holidays = holiday.count()
        return holidays
    
    def get_dateabsent(self,obj):
        today = datetime.date.today()
        student = models.StudentAttendance.objects.filter(student = obj.id,date__lte=today, date__month = today.month,date__year=today.year,present=False)
        date = []
        for i in student:
            if i.date not in date:
                date.append(i.date)
        return date

    def get_daysabsent(self,obj):
        today = datetime.date.today()
        student = models.StudentAttendance.objects.filter(student = obj.id,date__lte=today, date__month = today.month,date__year=today.year,present=False)
        days=[]
        for z in student:
            if z.date not in days:
                days.append(z.date)
        return len(days)

class StudentCard(serializers.ModelSerializer):

    Subdetails = serializers.SerializerMethodField(read_only=True)
    due_fees = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.Student
        fields = ["id","name","image","gender","dob","Subdetails","due_fees","referral_code"]

    def get_Subdetails(self,obj):
        try:
            activeSub  =  models.PurchasedSubscription.objects.get(student=obj, active= True)
            active=True
        except ObjectDoesNotExist:
            activeSub  =  models.PurchasedSubscription.objects.filter(student=obj, active= False)
            active=False
            activeSub = activeSub[0]
        except:
            print("Issue here in student card")
        timeslot = list()
        print(activeSub.timeslots.all())
        for i in activeSub.timeslots.all():
            data={
                "starttime":i.start,
                "endtime":i.end
            }
            timeslot.append(data)
        data ={

            "join date":activeSub.date,
            "timeslots":timeslot,
            "due date":activeSub.due_date,
            "Total off time":activeSub.totalOffTime,
            "hoursRemain":activeSub.hoursRemain,
            "active":active
        }
        return data
    
    def get_due_fees(self, obj):
        subscriptions = models.PurchasedSubscription.objects.filter(student=obj)
        print(subscriptions)
        total_amount = subscriptions.aggregate(Sum('total_amount'))
        print(total_amount)
        total_amount = total_amount['total_amount__sum']
        if total_amount:
            payments = models.StudentPayment.objects.filter(purchased_subscription__in=subscriptions).aggregate(Sum('amount_paid'))
            payments = payments['amount_paid__sum']
            if payments:
                due = total_amount - payments
                return int(due)
            else:
                return total_amount
        else:
            return None


class StudentYearlyAttendance(serializers.ModelSerializer):
    info = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.Student
        fields = ["info"]

    def get_info(self,obj):
        today = datetime.date.today()
        info=list()
        for i in range(1,today.month+1):
            monthStart = today.replace(day=1,month=i)
            Sub = models.PurchasedSubscription.objects.filter(student = obj.id)
            Submonth = Sub.filter(Q(from_date__month=i)|Q(due_date__month=i)).order_by('due_date')
            inactiveDate =[]
            counter=1
            present = models.StudentAttendance.objects.filter(student = obj.id, date__month = monthStart.month,date__year=today.year,present=True)
            presentdays=[]
            for z in present:
                if z.date not in presentdays:
                    presentdays.append(z.date)
            absent = models.StudentAttendance.objects.filter(student = obj.id, date__month = monthStart.month,date__year=today.year,present=False)
            absentdays=[]
            for z in absent:
                if z.date not in absentdays:
                    absentdays.append(z.date)

            holiday = librarymodels.Holidays.objects.filter(library_branch=obj.library_branch,start__month = monthStart.month,start__year=today.year,active=True)
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
        return info
class offTimeSerializer(serializers.ModelSerializer):

    slot = coreserializers.TimeSlotSerializer()
    #student = StudentMinSerializer()
    class Meta:
        model = models.StudentOfftime
        fields = ["id","student","date","offtime","slot"]

class StudentAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.StudentAttendance
        fields = "__all__"

class StudentOfftimeSerializer(serializers.ModelSerializer):

    slot = coreserializers.TimeSlotSerializer()
    class Meta:
        model = models.StudentOfftime
        fields = "__all__"

class OwnerStudentAttendanceSerializer(serializers.ModelSerializer):

    student = StudentMinSerializer()
    slot = coreserializers.TimeSlotSerializer()

    class Meta:
        model = models.StudentAttendance
        fields = ["id","student","slot","present"]



class TrackTotalOfftimeSerailzier(serializers.ModelSerializer):

    student=StudentMinSerializer()
    class Meta:
        model = models.PurchasedSubscription
        fields = ["id","student",'totalOffTime','totalRollBack']

class StudentManageSubSerializer(serializers.ModelSerializer):
    due_days = serializers.SerializerMethodField(read_only=True)
    due_fees = serializers.SerializerMethodField(read_only=True)
    student = StudentMinSerializer(read_only=True)
    class Meta:
        model = models.PurchasedSubscription
        fields = ["id","student","shift_fees","locker_charges","due_days","due_fees"]

    def get_due_days(self, obj):
        if obj.due_date:
            today = datetime.date.today()
            days = (obj.due_date - today).days
            return int(days)
        else:
            return 0

    def get_due_fees(self, obj):
        payments = models.StudentPayment.objects.filter(purchased_subscription=obj).aggregate(Sum('amount_paid'))
        payments = payments['amount_paid__sum']
        if payments:
            due = obj.total_amount - payments
            return int(due)
        return obj.total_amount

class UBFPaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.StudentUBFPayment
        fields = "__all__"

class StudentListSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Student
        fields = ["id","name"]