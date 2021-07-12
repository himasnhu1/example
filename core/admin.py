from django.contrib import admin
from . import models
from import_export.admin import ImportExportModelAdmin


admin.site.site_header = 'S.R.M.S.'

class IncidentAdmin(admin.ModelAdmin):
    list_display = [
                    'ticket',
                    'title',
                    'active',
                    ]
    list_filter = [
                    'date',
                    'active',
                    ]
    search_fields = [
                    'ticket',
                    ]

admin.site.register(models.User)
admin.site.register(models.HigherEducation)
admin.site.register(models.ExamsPreparingFor)
admin.site.register(models.OpeningDays)
admin.site.register(models.TimeSlot)

admin.site.register(models.SubscriptionPlan)
admin.site.register(models.SubscriptionPayment)

admin.site.register(models.Incident,IncidentAdmin)
admin.site.register(models.FAQ)
#admin.site.register(models.Notification)

admin.site.register(models.CurrentAffairCategory)
admin.site.register(models.CurrentAffair)
admin.site.register(models.CurrentAffairImage)

admin.site.register(models.Ammenity)

admin.site.register(models.Notifications)


