from django.urls import path, include
from .views import *

urlpatterns = [
    path('api/rewards/system/',RewardSystemAPI.as_view()),
    path('api/rewards/claim-200/',ConvertingpointsAPI.as_view()),
    path('api/reward-code-list/',rewardcodeList.as_view()),
    path('api/referral-check/',ReferralcodeAPI.as_view()),

]