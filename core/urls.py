from django.urls import path, include
from .views import *
#app_name = 'core'


urlpatterns = [
    path('api/user/passwordset/', UserChangedPasswordAPI.as_view()),
    path('api/enquiry-email/',EnquiryEmailAPI.as_view()),
]