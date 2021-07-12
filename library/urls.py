from django.urls import path, include
from .views import *

urlpatterns = [
    path('api/owner/branch/', LibraryBranchListAPI.as_view()),                        #checked
    path('api/branch-locker/<int:id>/', LibraryBranchLockerListAPI.as_view()),        #checked
    path('api/branch-subscription/<int:id>/', LibraryBranchSubListAPI.as_view()),
    path('api/owner/switch-branch/', OwnerSwitchBranchAPI.as_view()),                  #checked


]