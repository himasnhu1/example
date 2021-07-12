from rest_framework import serializers
from ubfcore.serializers import *
from ubfquiz.serializers import *
import razorpay
from django.conf import settings
from student.serializers import *
from . import models

class UserCartSerializer(serializers.ModelSerializer):
    student = StudentMinSerializer(many=False, read_only = True)
    pdfs = PDFSerializer(many=True, read_only = True)
    mcqs = MCQSerializer(many=True, read_only = True)
    summaries = SummarySerializer(many=True, read_only = True)
    sessions = SessionSerializer(many=True, read_only = True)
    tests = QuizListSerializer(many=True, read_only = True)
    order_id = serializers.SerializerMethodField(read_only = True)
    total_amount = serializers.SerializerMethodField(read_only = True)
    final_amount = serializers.SerializerMethodField(read_only = True)
    promoCode = serializers.SerializerMethodField(read_only = True)

    class Meta:
        model = models.UserCart
        fields = ['id', 'student', 'pdfs', 'mcqs', 'summaries', 'sessions', 'start_date', 'ordered_date', 'ordered', 'tests', 'order_id', 'total_amount','final_amount','promoCode']

    def get_order_id(self, obj):
        amount = 0
        for pdf in obj.pdfs.all():
            amount += pdf.price
        for mcq in obj.mcqs.all():
            amount += mcq.price
        for summary in obj.summaries.all():
            amount += summary.price
        for session in obj.sessions.all():
            amount += session.price
        for test in obj.tests.all():
            amount += test.price
        if obj.promocode is not None:
            if obj.promocode.discountpercent is not None:
                discount = (obj.promocode.discountpercent * amount)/100
                amount=amount-discount
        elif obj.rewardcode is not None:
            amount=amount-obj.rewardcode.max_discount
        if amount>0:
            data = {
                "amount" : amount*100,
                "currency" : 'INR',
                "receipt" : str(obj.id),
                "payment_capture" : '1',
            }
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            order_id = client.order.create(data = data)
            obj.order_id = order_id["id"]
            obj.save()
            return order_id
        return None


    def get_total_amount(self, obj):
        amount = 0
        for pdf in obj.pdfs.all():
            amount += pdf.price
        for mcq in obj.mcqs.all():
            amount += mcq.price
        for summary in obj.summaries.all():
            amount += summary.price
        for session in obj.sessions.all():
            amount += session.price
        for test in obj.tests.all():
            amount += test.price
        return amount
    
    def get_final_amount(self,obj):
        amount = 0
        for pdf in obj.pdfs.all():
            amount += pdf.price
        for mcq in obj.mcqs.all():
            amount += mcq.price
        for summary in obj.summaries.all():
            amount += summary.price
        for session in obj.sessions.all():
            amount += session.price
        for test in obj.tests.all():
            amount += test.price
        if obj.promocode is not None:            
            if obj.promocode.discountpercent is not None:
                discount = (obj.promocode.discountpercent * amount)/100
                amount=amount-discount
        elif obj.rewardcode is not None:
            amount=amount-obj.rewardcode.max_discount
        obj.amount = amount
        obj.save()
        return amount
        
    def get_promoCode(self,obj):
        if obj.promocode is not None:
            return obj.promocode.code
        elif obj.promocode is not None:
            return obj.rewardcode.code
        return None

class UserBookmarkSerializer(serializers.ModelSerializer):
    student = StudentMinSerializer(many=False, read_only = True)
    pdfs = PDFSerializer(many=True, read_only = True)
    mcqs = MCQSerializer(many=True, read_only = True)
    summaries = SummarySerializer(many=True, read_only = True)
    sessions = SessionSerializer(many=True, read_only = True)
    tests = QuizListSerializer(many=True, read_only = True)

    class Meta:
        model = models.Bookmark
        fields = ['id', 'student', 'pdfs', 'mcqs', 'summaries', 'sessions', 'tests']


class UserSaveForLaterSerializer(serializers.ModelSerializer):
    student = StudentMinSerializer(many=False, read_only = True)
    pdfs = PDFSerializer(many=True, read_only = True)
    mcqs = MCQSerializer(many=True, read_only = True)
    summaries = SummarySerializer(many=True, read_only = True)
    sessions = SessionSerializer(many=True, read_only = True)
    tests = QuizListSerializer(many=True, read_only = True)

    class Meta:
        model = models.SaveForLater
        fields = [ 'id', 'student', 'pdfs', 'mcqs', 'summaries', 'sessions', 'tests']

class PromocodeSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Promocode
        fields = ["id","code","title","description","validity"]