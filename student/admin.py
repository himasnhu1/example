from django.contrib import admin
from . import models
from import_export.admin import ImportExportModelAdmin

class StudentAdmin(ImportExportModelAdmin):
    list_display = [
                    'library_branch',
                    'name',
                    'mobile',
                    ]
    list_display_links = [
                    'library_branch',
                    'name',
                    'mobile',
                    ]
    list_filter = [
                    'library_branch',
                    'state',
                    'higher_education',
                    'exam_preparing_for',
                    'gender',
                    ]
    search_fields = [
                    'library_branch',
                    'name',
                    'mobile',
                    'state',
                    'higher_education',
                    'exam_preparing_for',
                    'address'
                    'location'
                    ]

class PurchasedSubscriptionAdmin(ImportExportModelAdmin):
    list_display = ['student','date','active']
    list_display_links = [
                    'student',

                    'date',
                    ]
    list_filter = [

                    ]
    search_fields = [
                    'student',

                    'date',
                    ]


class PaymentAdmin(ImportExportModelAdmin):
    list_display = [
        'purchased_subscription',
        'amount_paid',
        'date',
        'payment_mode',
    ]
    list_display_links = [
        'purchased_subscription',
        'amount_paid',
        'date',
        'payment_mode',
    ]
    list_filter = [
        'purchased_subscription',
        'amount_paid',
        'date',
        'payment_mode',
    ]
    search_fields = [
        'purchased_subscription',
        'amount_paid',
        'date',
        'payment_mode',
    ]

class OfftimeAdmin(ImportExportModelAdmin):
    list_display=["student","date","offtime"]
    search_fields =["student","date","offtime"]

admin.site.register(models.Student, StudentAdmin)
admin.site.register(models.StudentAttendance)
admin.site.register(models.PurchasedSubscription, PurchasedSubscriptionAdmin)
admin.site.register(models.StudentPayment, PaymentAdmin)
admin.site.register(models.StudentOfftime, OfftimeAdmin)
admin.site.register(models.StudentUBFPayment)