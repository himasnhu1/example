from django.contrib import admin
from django.contrib.auth.models import Group
import nested_admin
from . import models


class PDFInline(nested_admin.NestedTabularInline):
	model = models.PDF
	extra = 4


class MCQInline(nested_admin.NestedTabularInline):
	model = models.MCQ
	extra = 4


class SummaryInline(nested_admin.NestedTabularInline):
	model = models.Summary
	extra = 4



class SubCategoryInline(nested_admin.NestedTabularInline):
	model = models.SubCategory
	inlines = [PDFInline,SummaryInline, MCQInline]
	extra = 5


class CategoryAdmin(nested_admin.NestedModelAdmin):
	inlines = [SubCategoryInline,]


class SubCategoryAdmin(nested_admin.NestedModelAdmin):
    inlines = [PDFInline, SummaryInline, MCQInline]

admin.site.register(models.Category, CategoryAdmin)
admin.site.register(models.SubCategory, SubCategoryAdmin)
admin.site.register(models.PDF)
admin.site.register(models.MCQ)
admin.site.register(models.Summary)
admin.site.register(models.Session)
admin.site.register(models.UserSubscriptions)

admin.site.register(models.GeneralNotification)
#admin.site.register(models.PersonalNotification)
#admin.site.register(models.PromoCode)
#admin.site.register(models.UserCode)