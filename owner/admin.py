from django.contrib import admin
from . import models
from import_export.admin import ImportExportModelAdmin

class OwnerAdmin(ImportExportModelAdmin):
    list_display = [
                    'name',
                    'mobile',
                    ]
    list_display_links = [
                    'name',
                    'mobile',
                    ]
    list_filter = [
                    'state',
                    ]
    search_fields = [
                    'name',
                    'mobile',
                    'alternate_mobile',
                    'email',
                    'address',
                    'city',
                    'state',
                    'pincode',
                    'location',
                    ]

class EmployeeAdmin(ImportExportModelAdmin):
    list_display = [
                    'name',
                    'mobile',
                    ]
    list_display_links = [
                    'name',
                    'mobile',
                    ]
    list_filter = [
                    'state',
                    ]
    search_fields = [
                    'name',
                    'mobile',
                    'alternate_mobile',
                    'email',
                    'address',
                    'city',
                    'state',
                    'pincode',
                    'location',
                    ]

class EnquiryAdmin(ImportExportModelAdmin):
    list_display = [
                    'library_branch',
                    'name',
                    ]
    list_display_links = [
                    'library_branch',
                    'name',
                    ]
    list_filter = [
                    ]
    search_fields = [
                    'library_branch',
                    'student',
                    'comment',
                    ]

class ExpenseAdmin(ImportExportModelAdmin):
    list_display = [
                    'library_branch',
                    'title',
                    'amount_paid',
                    ]
    list_display_links = [
                    'library_branch',
                    'title',
                    'amount_paid',
                    ]
    list_filter = [
                    'library_branch',
                    'payment_mode',
                    ]
    search_fields = [
                    'title',
                    'amount_paid',
                    'note',
                    ]


admin.site.register(models.Owner, OwnerAdmin)
admin.site.register(models.UserLibraryPermissions)
admin.site.register(models.Employee, EmployeeAdmin)
admin.site.register(models.Enquiry, EnquiryAdmin)
admin.site.register(models.EnquiryFollowUp)
admin.site.register(models.Expense, ExpenseAdmin)
admin.site.register(models.Feedback)
admin.site.register(models.FeedbackFollowUp)
admin.site.register(models.OwnerSubscriptionPlan)
admin.site.register(models.Ownerpayment)
admin.site.register(models.OwnerDevice)
admin.site.register(models.OwnerSubPlan)