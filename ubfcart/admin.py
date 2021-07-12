from django.contrib import admin
from .models import *


admin.site.register(UserCart)
admin.site.register(Bookmark)
admin.site.register(SaveForLater)
admin.site.register(Payment)
admin.site.register(Promocode)