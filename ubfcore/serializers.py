from rest_framework import serializers
from ubfquiz import models as ubfquizmodels
from . import models
from django.conf import settings

from ubfquiz import serializers as ubfquizserial
from student import models as studentmodels
from student import serializers as studentserializers

import datetime
from datetime import datetime,timedelta,date
from pytz import timezone

class SubCategorySerializer(serializers.ModelSerializer):
    # url = serializers.HyperlinkedIdentityField(view_name="core:sub-category-detail")

    class Meta:
        model = models.SubCategory
        fields = ['id', 'name']
class CategorySerializer(serializers.ModelSerializer):
    # url = serializers.HyperlinkedIdentityField(view_name="core:category-detail")
    subCategory = serializers.SerializerMethodField()
    class Meta:
        model = models.Category
        fields = ['id', 'name','subCategory']

    def get_subCategory(self,obj):

        sub = models.SubCategory.objects.filter(category=obj)
        serializer = SubCategorySerializer(sub,many=True)

        return (serializer.data)

class ArticleSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Article
        fields = ['id', 'title', 'image', 'date', 'content']
class PDFSerializer(serializers.ModelSerializer):
    # url = serializers.HyperlinkedIdentityField(view_name="core:pdf-detail")
    sub_category = SubCategorySerializer(many=False, read_only = True)
    type = serializers.SerializerMethodField(read_only = True)

    class Meta:
        model = models.PDF
        fields = [ 'id', 'name', 'file', 'price', 'sub_category', 'type']

    def get_type(self, obj):
        return "pdf"

class PDFListSerializer(serializers.ModelSerializer):

    sub_category = SubCategorySerializer(many=False, read_only = True)
    type = serializers.SerializerMethodField(read_only = True)
    file = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.PDF
        fields = ['id', 'name', 'price', 'sub_category', 'file', 'type']

    def get_type(self, obj):
        return "pdf"

    def get_file(self,obj):

        if obj.price<1:
            file =self.context['request'].build_absolute_uri(obj.file.url)
            # return obj.file.url
            return file
        
        user = self.context['request'].user
        if user.id is not None:
            try:
                student = studentmodels.Student.objects.get(user = user)
            except:
                return None
            sub = models.UserSubscriptions.objects.get(student = student)
            if obj in sub.pdfs.all():
                file =self.context['request'].build_absolute_uri(obj.file.url)
                # return obj.file.url
                return file
        else:
            return None

class MCQSerializer(serializers.ModelSerializer):

    sub_category = SubCategorySerializer(many=False, read_only = True)
    type = serializers.SerializerMethodField(read_only = True)

    class Meta:
        model = models.MCQ
        fields = ['id', 'name', 'file', 'price', 'sub_category', 'image', 'preview_file', 'description', 'type']

    def get_type(self, obj):
        return "mcq"

class MCQListSerializer(serializers.ModelSerializer):

    sub_category = SubCategorySerializer(many=False, read_only = True)
    type = serializers.SerializerMethodField(read_only = True)
    file = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.MCQ
        fields = [ 'id', 'file', 'name', 'price', 'sub_category', 'image', 'preview_file', 'description', 'type', "file"]

    def get_type(self, obj):
        return "mcq"

    def get_file(self,obj):

        if obj.price<1:
            file =self.context['request'].build_absolute_uri(obj.file.url)
            # return obj.file.url
            return file
        
        user = self.context['request'].user
        if user.id is not None:
            try:
                student = studentmodels.Student.objects.get(user = user)
            except:
                return None
            sub = models.UserSubscriptions.objects.get(student = student)
            if obj in sub.mcqs.all():
                file =self.context['request'].build_absolute_uri(obj.file.url)
                # return obj.file.url
                return file
        else:
            return None

class SummarySerializer(serializers.ModelSerializer):
    # url = serializers.HyperlinkedIdentityField(view_name="core:summary-detail")
    sub_category = SubCategorySerializer(many=False, read_only = True)
    mcq = MCQSerializer(many=True, read_only = True)
    type = serializers.SerializerMethodField(read_only = True)

    class Meta:
        model = models.Summary
        fields = ['id', 'name', 'file', 'price', 'sub_category', 'description','mcq', 'image', 'preview_file', 'type']

    def get_type(self, obj):
        return "summary"

class SummaryListSerializer(serializers.ModelSerializer):
    # url = serializers.HyperlinkedIdentityField(view_name="core:summary-detail")
    sub_category = SubCategorySerializer(many=False, read_only = True)
    mcq = MCQListSerializer(many=True, read_only = True)
    type = serializers.SerializerMethodField(read_only = True)
    file = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.Summary
        fields = ['id', 'name', 'price', 'sub_category', 'description','mcq',  'image', 'preview_file', 'type',"file"]

    def get_type(self, obj):
        return "summary"
    
    def get_file(self,obj):

        if obj.price<1:
            file =self.context['request'].build_absolute_uri(obj.file.url)
            # return obj.file.url
            return file
        
        user = self.context['request'].user
        if user.id is not None:
            try:
                student = studentmodels.Student.objects.get(user = user)
            except:
                return None
            sub = models.UserSubscriptions.objects.get(student = student)
            if obj in sub.summaries.all():
                file =self.context['request'].build_absolute_uri(obj.file.url)
                # return obj.file.url
                return file
        else:
            return None

class SessionSerializer(serializers.ModelSerializer):
    # url = serializers.HyperlinkedIdentityField(view_name="core:session-detail")
    type = serializers.SerializerMethodField(read_only = True)
    upcoming = serializers.SerializerMethodField(read_only = True)
    
    class Meta:
        model = models.Session
        fields = ['id', 'name', 'image', 'price', 'date', 'video','youtube_link', 'type', 'upcoming', 'demo']

    def get_type(self, obj):
        return "session"

    def get_upcoming(self, obj):
        if obj.date > date.today():
            return True
        else:
            return False

class SessionListSerializer(serializers.ModelSerializer):
    # url = serializers.HyperlinkedIdentityField(view_name="core:session-detail")
    type = serializers.SerializerMethodField(read_only = True)
    upcoming = serializers.SerializerMethodField(read_only = True)
    file = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = models.Session
        fields = ['id', 'name', 'image', 'price', 'date','youtube_link', 'type', 'upcoming', 'demo',"file"]

    def get_type(self, obj):
        return "session"

    def get_upcoming(self, obj):
        if obj.date > date.today():
            return True
        else:
            return False
    
    def get_file(self,obj):

        if obj.price<1:
            file =self.context['request'].build_absolute_uri(obj.video.url)
            # return obj.file.url
            return file
        
        user = self.context['request'].user
        if user.id is not None:
            try:
                student = studentmodels.Student.objects.get(user = user)
            except:
                return None
            sub = models.UserSubscriptions.objects.get(student = student)
            if obj in sub.sessions.all():
                file =self.context['request'].build_absolute_uri(obj.video.url)
                # return obj.file.url
                return file
        else:
            return None

class UserSubscriptionsSerializer(serializers.ModelSerializer):
    # url = serializers.HyperlinkedIdentityField(view_name="core:user-subscription-detail")
    student = studentserializers.StudentMinSerializer(many=False, read_only = True)
    pdfs = PDFSerializer(many=True, read_only = True)
    mcqs = MCQListSerializer(many=True, read_only = True)
    summaries = SummaryListSerializer(many=True, read_only = True)
    sessions = SessionListSerializer(many=True, read_only = True)
    tests = ubfquizserial.QuizListSerializer(many=True, read_only = True)
    # quizinfo = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.UserSubscriptions
        fields = ['id', 'student', 'pdfs', 'mcqs', 'summaries', 'sessions','tests']

class SearchSerializer(serializers.Serializer):

    pdfs = serializers.SerializerMethodField('get_pdfs')
    mcqs = serializers.SerializerMethodField('get_mcqs')
    summaries = serializers.SerializerMethodField('get_summaries')
    sessions = serializers.SerializerMethodField('get_sessions')
    tests = serializers.SerializerMethodField('get_tests')

    class Meta:
        fields =["pdfs","mcqs","summaries","sessions","tests"]

    def get_pdfs(self,obj):
        serializer_context = {'request': self.context.get('request') }
        queryset = obj.pdfs
        serializer = PDFListSerializer(queryset, many=True, context=serializer_context)
        return serializer.data

    def get_mcqs(self,obj):
        serializer_context = {'request': self.context.get('request') }
        queryset = obj.mcqs
        serializer = MCQListSerializer(queryset, many=True, context=serializer_context)
        return serializer.data

    def get_summaries(self,obj):
        serializer_context = {'request': self.context.get('request') }
        queryset = obj.summaries
        serializer = SummaryListSerializer(queryset, many=True, context=serializer_context)
        return serializer.data

    def get_sessions(self,obj):
        serializer_context = {'request': self.context.get('request') }
        queryset = obj.sessions
        serializer = SessionListSerializer(queryset, many=True, context=serializer_context)
        return serializer.data

    def get_tests(self,obj):
        serializer_context = {'request': self.context.get('request') }
        queryset = obj.tests
        serializer = ubfquizserial.QuizListSerializer(queryset, many=True, context=serializer_context)
        return serializer.data
class GeneralNotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.GeneralNotification
        fields = '__all__'

# class PersonalNotification(serializers.ModelSerializer):

#     class Meta:
#         model = models.PersonalNotification
#         fields = '__all__'

# class Personalnotif(serializers.ModelSerializer):

# #    quiz = QuizMInSerializer(many=True)
#     quizinfo = serializers.SerializerMethodField()
#     duration = serializers.SerializerMethodField()
#     quizname = serializers.SerializerMethodField()
#     quizslug = serializers.SerializerMethodField()
#     class Meta:

#         model = models.PersonalNotification
#         fields = '__all__'
    
#     def get_quizinfo(self,obj):

#         now = datetime.now()
#         quiz = Quiz.objects.get(id=obj.quiz_id)

#         quizSlot =  QuizSlot.objects.filter(quiz=quiz)
#         for slot in quizSlot:
#             if now>=slot.start_datetime and now<=(slot.start_datetime+quiz.duration):
#                 data={
#                     "date":(slot.start_datetime+timedelta(hours=5,minutes=30)).strftime("%b %d %Y"),
#                     "time":(slot.start_datetime+timedelta(hours=5,minutes=30)).strftime("%H:%M:%S")
#                 }
#                 return data
#             elif now<slot.start_datetime and now<(slot.start_datetime+quiz.duration):
#                 data={
#                     "date":(slot.start_datetime+timedelta(hours=5,minutes=30)).strftime("%b %d %Y"),
#                     "time":(slot.start_datetime+timedelta(hours=5,minutes=30)).strftime("%H:%M:%S")
#                 }
#                 return data

#     def get_duration(self,obj):
#         quiz = Quiz.objects.get(id=obj.quiz_id)

#         return (str(quiz.duration))
    
#     def get_quizname(self,obj):
#         quiz = Quiz.objects.get(id=obj.quiz_id)

#         return quiz.name
#     def get_quizslug(self,obj):
#         quiz = Quiz.objects.get(id=obj.quiz_id)

#         return quiz.slug

# class PromoUser(serializers.ModelSerializer):

#     class Meta:
#         model = models.UserCode
#         fields = "__all__"

# class PromoCode(serializers.ModelSerializer):

#     class Meta:
#         model=models.PromoCode
#         fields='__all__'















