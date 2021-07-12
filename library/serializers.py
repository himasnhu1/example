from rest_framework import serializers
from . import models
from django.contrib.auth.models import User
import datetime
from core import models as coremodels
from core import serializers as coreserializers

from student import models as studentmodels
from student import serializers as studentserializers

class LibrarySerializer(serializers.ModelSerializer):
    # url = serializers.HyperlinkedIdentityField(view_name="library-detail")

    class Meta:
        model = models.Library
        fields = "__all__"




class LibraryBranchSerializer(serializers.ModelSerializer):
    # url = serializers.HyperlinkedIdentityField(view_name="librarybranch-detail")
    lockers = serializers.SerializerMethodField(read_only=True)
    fees = serializers.SerializerMethodField(read_only=True)
    # time_slots = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.LibraryBranch
        fields = "__all__"

    def get_lockers(self, obj):
        lockers = models.LibraryLocker.objects.filter(library_branch = obj)
        serializer = LibraryLockerSerializer(lockers, many=True)
        return serializer.data

    def get_fees(self, obj):
        data = {}
        subscriptions = models.LibrarySubscription.objects.filter(library_branch = obj)
        for i in range(1, 25):
            subscription = subscriptions.filter(no_of_hours = i)
            if subscription.exists():
                today = datetime.datetime.today()
                if obj.beginning_of_summer_season <= int(today.month) < obj.beginning_of_winter_season:
                    data[i] = subscription[0].summer_base_charges
                else:
                    data[i] = subscription[0].winter_base_charges
        return data

    # def get_time_slots(self, obj):
    #     data = {}
    #     timeslots = coremodels.TimeSlot.objects.all()
    #     for timeslot in timeslots:
    #         timeslot_data = coreserializers.TimeSlotSerializer(timeslot, many=False).data
    #         data[timeslot.id] = {
    #             "timeslot": timeslot_data,
    #             "available": 10,
    #             "filled": 20,
    #             "total": int(obj.seat_capacity)
    #         }
    #     print(data)
    #     return data

class LibraryLockerSerializer(serializers.ModelSerializer):
    # url = serializers.HyperlinkedIdentityField(view_name="librarylocker-detail")
    student_details = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.LibraryLocker
        fields = "__all__"

    def get_student_details(self, obj):
        if obj.assigned_student:
            serializer = studentserializers.StudentSerializer(obj.assigned_student, many=False)
            return serializer.data
        else:
            return None

class LibrarySubscriptionSerializer(serializers.ModelSerializer):
    # url = serializers.HyperlinkedIdentityField(view_name="librarysubscription-detail")

    class Meta:
        model = models.LibrarySubscription
        fields = "__all__"

class UpcomingHolidaysSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = models.Holidays
        fields = "__all__"
class HolidaysSerializer(serializers.ModelSerializer):
    # url = serializers.HyperlinkedIdentityField(view_name="holidays-detail")

    upcoming_holidays = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = models.Holidays
        fields = "__all__"
    
    def get_upcoming_holidays(self, obj):
        holiday = models.Holidays.objects.filter(start__lte=datetime.datetime.today())[0:5]
        serializer = UpcomingHolidaysSerializer(holiday, many=True)
        return serializer.data

class LibraryOfferSerializer(serializers.ModelSerializer):
    # url = serializers.HyperlinkedIdentityField(view_name="libraryoffer-detail")
    class Meta:
        model = models.LibraryOffer
        fields = "__all__"

class QrcodeSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.AttendanceQrCode
        fields = "__all__"        

class MinLibraryBranchSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.LibraryBranch
        fields = "__all__"

class MinLibraryLockerSerializer(serializers.ModelSerializer):
    studentDetails = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.LibraryLocker
        fields = "__all__"

    def get_studentDetails(self, obj):
        if obj.assigned_student:
            serializer = studentserializers.StudentMinSerializer(obj.assigned_student, many=False)
            return serializer.data
        else:
            return None  

class BranchSwitchSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.LibraryBranch
        fields = ["id","name"]