from rest_framework import serializers
from . import models
from django.contrib.auth.models import User
from library import serializers as libraryserializers
import datetime
from student import serializers as studentserializer
import razorpay
from django.conf import settings

class OwnerSerializer(serializers.ModelSerializer):
    #url = serializers.HyperlinkedIdentityField(view_name="owner-detail")

    class Meta:
        model = models.Owner
        fields = "__all__"

class OwnerMinSerializer(serializers.ModelSerializer):
    #url = serializers.HyperlinkedIdentityField(view_name="owner-detail")

    class Meta:
        model = models.Owner
        fields = ["name","id","branches"]

class UserLibraryPermissionsSerializer(serializers.ModelSerializer):
    #url = serializers.HyperlinkedIdentityField(view_name="userlibrarypermissions-detail")

    class Meta:
        model = models.UserLibraryPermissions
        fields = "__all__"

class EmployeeSerializer(serializers.ModelSerializer):
    #url = serializers.HyperlinkedIdentityField(view_name="employee-detail")
    # branches = libraryserializers.LibraryBranchSerializer(many=True)

    class Meta:
        model = models.Employee
        fields = "__all__"

class EnquirySerializer(serializers.ModelSerializer):
    #url = serializers.HyperlinkedIdentityField(view_name="enquiry-detail")
    days = serializers.SerializerMethodField(read_only=True)
    follow_ups = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = models.Enquiry
        fields = "__all__"

    def get_days(self, obj):
        today = datetime.date.today()
        days = (obj.follow_up_date - today).days
        return days

    def get_follow_ups(self, obj):
        follow_ups = models.EnquiryFollowUp.objects.filter(enquiry = obj)
        serializer = EnquiryFollowUpSerializer(follow_ups, many=True)
        return serializer.data

class EnquiryFollowUpSerializer(serializers.ModelSerializer):
    # url = serializers.HyperlinkedIdentityField(view_name="enquiryfollowup-detail")

    class Meta:
        model = models.EnquiryFollowUp
        fields = "__all__"

class ExpenseSerializer(serializers.ModelSerializer):
    #url = serializers.HyperlinkedIdentityField(view_name="expense-detail")

    class Meta:
        model = models.Expense
        fields = "__all__"

class FeedbackSerializer(serializers.ModelSerializer):
    #url = serializers.HyperlinkedIdentityField(view_name="libraryfeedback-detail")
    days = serializers.SerializerMethodField(read_only=True)
    #follow_ups = serializers.SerializerMethodField(read_only=True)
    student_detail = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.Feedback
        fields = "__all__"

    def get_days(self, obj):
        today = datetime.date.today()
        days = (obj.date-today).days
        return int(days)

    # def get_follow_ups(self, obj):
    #     follow_ups = models.FeedbackFollowUp.objects.filter(feedback = obj)
    #     serializer = FeedbackFollowUpSerializer(follow_ups, many=True)
    #     return serializer.data

    def get_student_detail(self, obj):
        serializer = studentserializer.StudentMinSerializer(obj.student, many=False)
        return serializer.data

class FeedbackFollowUpSerializer(serializers.ModelSerializer):
    # url = serializers.HyperlinkedIdentityField(view_name="feedbackfollowup-detail")

    class Meta:
        model = models.FeedbackFollowUp
        fields = "__all__"

class EmployeeFeedbackFollowUpSerializer(serializers.ModelSerializer):
    # url = serializers.HyperlinkedIdentityField(view_name="feedbackfollowup-detail")

    class Meta:
        model = models.EmployeeFeedbackFollowUp
        fields = "__all__"
class EmployeeFeedbackSerializer(serializers.ModelSerializer):
    #url = serializers.HyperlinkedIdentityField(view_name="libraryfeedback-detail")
    days = serializers.SerializerMethodField(read_only=True)
    follow_ups = serializers.SerializerMethodField(read_only=True)
    employee_detail = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.EmployeeFeedback
        fields = "__all__"

    def get_days(self, obj):
        today = datetime.date.today()
        days = (today - obj.date).days
        return int(days)

    def get_follow_ups(self, obj):
        follow_ups = models.EmployeeFeedbackFollowUp.objects.filter(feedback = obj)
        serializer = EmployeeFeedbackFollowUpSerializer(follow_ups, many=True)
        return serializer.data

    def get_employee_detail(self, obj):
        serializer = EmployeeSerializer(obj.employee, many=False)
        return serializer.data

class OnwerExpenseSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Expense
        fields = ["id","library_branch","title","amount_paid","payment_mode","invoice","date"]

class FeedbackMinSerializer(serializers.ModelSerializer):
    days = serializers.SerializerMethodField(read_only=True)
    student = studentserializer.StudentMinSerializer(read_only=True)

    class Meta:
        model = models.Feedback
        fields = "__all__"

    def get_days(self, obj):
        today = datetime.date.today()
        days = (obj.date - today).days
        return int(days)

class OnwerExpenseListSerializer(serializers.ModelSerializer):

    type = serializers.SerializerMethodField()
    class Meta:
        model = models.Expense
        fields = ["id","title","amount_paid","type","date"]

    def get_type(self,obj):
        return str("Expense")

class OnwerSubscriptionSerializer(serializers.ModelSerializer):

    order_id = serializers.SerializerMethodField(read_only = True)
    class Meta:
        model = models.OwnerSubscriptionPlan
        fields ='__all__'
    
    def get_order_id(self, obj):
        data = {
            "amount" : obj.amount*100,
            "currency" : 'INR',
            "receipt" : str(obj.id),
            "payment_capture" : '1',
        }
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        order_id = client.order.create(data = data)
        obj.order_id = order_id["id"]
        obj.save()
        return order_id  

class OnwerSubscriptionViewSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.OwnerSubscriptionPlan
        fields ='__all__'

class OwnerDeviceSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.OwnerDevice
        fields = '__all__'

class OwnerSubPlanSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.OwnerSubPlan
        fields = '__all__'