from allauth.account.adapter import get_adapter
from rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from . import models
from django.contrib.auth.models import User
from fcm.models import Device



class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.User
        fields = ('email', 'username', 'password', 'is_student', 'is_owner', 'is_admin', 'is_employee', 'notification_token','passwordchanged')

class CustomRegisterSerializer(RegisterSerializer):
    is_student = serializers.BooleanField()
    is_owner = serializers.BooleanField()
    is_employee = serializers.BooleanField()
    is_admin = serializers.BooleanField()
    notification_token = serializers.CharField(max_length = 64, allow_blank=True, allow_null=True)
    passwordchanged = serializers.BooleanField()

    class Meta:
        model = models.User
        fields = ('email', 'username', 'password', 'is_student', 'is_owner', 'is_admin', 'is_employee', 'notification_token','passwordchanged')

    def get_cleaned_data(self):
        return {
            'username': self.validated_data.get('username', ''),
            'password1': self.validated_data.get('password1', ''),
            'password2': self.validated_data.get('password2', ''),
            'email': self.validated_data.get('email', ''),
            'is_student': self.validated_data.get('is_student', ''),
            'is_owner': self.validated_data.get('is_owner', ''),
            'is_employee': self.validated_data.get('is_employee', ''),
            'is_admin': self.validated_data.get('is_admin', ''),
            'notification_token': self.validated_data.get('notification_token', ''),
            'passwordchanged': self.validated_data.get('passwordchanged', ''),
        }

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        user.is_student = self.cleaned_data.get('is_student')
        user.is_owner = self.cleaned_data.get('is_owner')
        user.is_admin = self.cleaned_data.get('is_admin')
        user.is_employee = self.cleaned_data.get('is_employee')
        user.notification_token = self.cleaned_data.get('notification_token')
        user.passwordchanged = self.cleaned_data.get('passwordchanged')
        user.save()
        adapter.save_user(request, user, self)
        return user

class TokenSerializer(serializers.ModelSerializer):
    user_type = serializers.SerializerMethodField()
    notification_token = serializers.SerializerMethodField()
    passwordchanged = serializers.SerializerMethodField()

    class Meta:
        model = Token
        fields = ('key', 'user', 'user_type', 'notification_token','passwordchanged')

    def get_user_type(self, obj):
        serializer_data = UserSerializer(
            obj.user
        ).data
        is_student = serializer_data.get('is_student')
        is_owner = serializer_data.get('is_owner')
        is_admin = serializer_data.get('is_admin')
        is_employee = serializer_data.get('is_employee')
        return {
            'is_student': is_student,
            'is_owner': is_owner,
            'is_admin': is_admin,
            'is_employee': is_employee,
        }
    
    def get_notification_token(self, obj):
        serializer_data = UserSerializer(
            obj.user
        ).data
        notification_token = serializer_data.get('notification_token')
        return notification_token

    def get_passwordchanged(self, obj):
        serializer_data = UserSerializer(
            obj.user
        ).data
        passwordchanged = serializer_data.get('passwordchanged')
        return passwordchanged

class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MyDevice
        fields = ('dev_id','reg_id','user','name','is_active')

class HigherEducationSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="highereducation-detail")

    class Meta:
        model = models.HigherEducation
        fields = "__all__"


class ExamsPreparingForSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="examspreparingfor-detail")

    class Meta:
        model = models.ExamsPreparingFor
        fields = "__all__"


class OpeningDaysSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="openingdays-detail")

    class Meta:
        model = models.OpeningDays
        fields = "__all__"


class TimeSlotSerializer(serializers.ModelSerializer):
    # url = serializers.HyperlinkedIdentityField(view_name="timeslot-detail")

    class Meta:
        model = models.TimeSlot
        fields = "__all__"


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    # url = serializers.HyperlinkedIdentityField(view_name="subscriptionplan-detail")

    class Meta:
        model = models.SubscriptionPlan
        fields = "__all__"


class SubscriptionPaymentSerializer(serializers.ModelSerializer):
    # url = serializers.HyperlinkedIdentityField(view_name="subscriptionpayment-detail")
    subscription_plan = SubscriptionPlanSerializer(many=False)

    class Meta:
        model = models.SubscriptionPayment
        fields = "__all__"


class FeedbackSerializer(serializers.ModelSerializer):
    # url = serializers.HyperlinkedIdentityField(view_name="feedback-detail")

    class Meta:
        model = models.Feedback
        fields = "__all__"

class IncidentSerializer(serializers.ModelSerializer):
    # url = serializers.HyperlinkedIdentityField(view_name="incident-detail")

    class Meta:
        model = models.Incident
        fields = "__all__"


class FAQSerializer(serializers.ModelSerializer):
    # url = serializers.HyperlinkedIdentityField(view_name="faq-detail")

    class Meta:
        model = models.FAQ
        fields = "__all__"


class NotificationSerializer(serializers.ModelSerializer):
    # url = serializers.HyperlinkedIdentityField(view_name="notification-detail")

    class Meta:
        model = models.Notification
        fields = "__all__"


class CurrentAffairCategorySerializer(serializers.ModelSerializer):
    # url = serializers.HyperlinkedIdentityField(view_name="currentaffaircategory-detail")

    class Meta:
        model = models.CurrentAffairCategory
        fields = "__all__"


class CurrentAffairSerializer(serializers.ModelSerializer):
    # url = serializers.HyperlinkedIdentityField(view_name="currentaffair-detail")
    image = serializers.SerializerMethodField()
    # category = serializers.HyperlinkedRelatedField(many=False, view_name='current-affairs-category-detail', read_only=True)
    # category = CurrentAffairCategorySerializer(many=False)

    class Meta:
        model = models.CurrentAffair
        fields = ['url', 'id', 'category', 'title', 'posted_by', 'description', 'image']

    def get_image(self, obj):
        images = models.CurrentAffairImage.objects.filter(current_affair=obj)
        serializer = CurrentAffairImageSerializer(images, many=True)
        return serializer.data

class CurrentAffairImageSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="currentaffairimage-detail")

    class Meta:
        model = models.CurrentAffairImage
        fields = "__all__"

class AmmenitiesSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="ammenity-detail")

    class Meta:
        model = models.Ammenity
        fields = "__all__"

class StudentNotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Notifications
        fields = '__all__'

