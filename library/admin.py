from django.contrib import admin
from . import models
from import_export.admin import ImportExportModelAdmin
# Register your models here.


class LibraryBranchAdmin(ImportExportModelAdmin):
    list_display = [
                    'name',
                    ]
    list_display_links =[
                    'name',

                    ]
    list_filter = [

                    ]
    search_fields = [
                    'name',
                    ]

class QrcodeAdmin(ImportExportModelAdmin):
    list_display = ['branch','qrcode']

admin.site.register(models.Library)
admin.site.register(models.LibraryBranch, LibraryBranchAdmin)
admin.site.register(models.LibraryLocker)
admin.site.register(models.LibrarySubscription)
admin.site.register(models.Holidays)
admin.site.register(models.LibraryOffer)
admin.site.register(models.AttendanceQrCode,QrcodeAdmin)