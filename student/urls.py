from django.urls import path, include
from .studentcornerapi import *
from .ownerapi import *
#from .views import *

urlpatterns = [
    path('api/employee/<int:id>/studentcorner/', StudentAPIViewSet.as_view()),
    path('api/employee/<int:id>/studentcorner/<int:pk>/',StudentCornerDetailAPI.as_view(), name='student-corner-detail'),
    path('api/employee/<int:id>/studentcorner/<int:pk>/history/',StudentSubDetailAPI.as_view(), name='student-corner-history'),
    path('api/employee/<int:id>/studentcorner/<int:pk>/active-sub/',StudentActiveSubDetailAPI.as_view(), name='student-corner-active-sub'),

    #TodaysFollowupDue

    path('api/employee/<int:id>/todayfollowup-count/',TodayDueCountAPI.as_view()),
    path('api/employee/<int:id>/todayfollowup/dues/',TodayDuefeeAPI.as_view()),
    path('api/employee/<int:id>/todayfollowup/dues/<int:pk>/',TodayDuefeeClearApi.as_view()),

    #OffTime
    path('api/employee/<int:id>/studentofftime/today/',TrackStudentOfftimeTodayAPI.as_view()),
    path('api/employee/<int:id>/studentofftime/total/',TrackStudentOfftimeListAPI.as_view()),
    path('api/employee/<int:id>/studentofftime/total/<int:pk>/',TrackStudentOfftimeListAPI.as_view()),
    path('api/employee/<int:id>/studentofftime/total/details/<int:pk>/',SingleStudentOfftime.as_view()),

    path('api/employee/<int:id>/studentofftime/today-count/',TrackStudentofftimeTodayCountAPI.as_view()),

    #web student apis

    path('api/student/student-profile/<int:pk>/',StudentDetailAPI.as_view()),
    path('api/student/student-profile/<int:pk>/currentsub/',StudentActiveSubDetailAPI.as_view()),
    path('api/student/student-profile/<int:pk>/history/',StudentSubDetailAPI.as_view()),
    path('api/student/monthly-attendance/',StudentAttendanceStatus.as_view()),
    path('api/student/studentcard/',StudentCard.as_view()), 
    path('api/student/studentattendance/',StudentAttendanceAPI.as_view()),
    path('api/student/studentofftime/',StudentOfftimeAPI.as_view()),

    path('api/owner/<int:id>/studentattendance/',OwnerStudentAttendanceAPI.as_view()), ##screen 99
    path('api/owner/<int:id>/studentattendance/close/<int:pk>/',OwnerStudentAttendanceUpdateAPI.as_view()),

    path('api/student-attendance-check/',StudentAttendanceOfftimeCheckAPI.as_view()),           ## Student Qrcode Checker

    path('api/student-notification/',NotificationCentreAPI.as_view()),  ## For list
    path('api/student-notification/<int:id>/',NotificationCentreAPI.as_view()), ##for deleting the message

    path('api/student-manage-pendings/<int:id>/',StudentManagePendingsAPI.as_view()), ##screen 76  ##removed 
    path('api/student-newadmission/<int:id>/',NewAdmissionListAPI.as_view()),   ### remove it
    path('api/student-newrenewal/<int:id>/',StudentRenewalListAPI.as_view()),   ##removed

    path('api/student-newadmission-csv/<int:id>/',NewAdmissionCSVAPI.as_view()),   ##remove it
    path('api/student-newadmission-mailcsv/<int:id>/',NewAdmissionCSVMailAPI.as_view()), ##remove it

    path('api/employee/<int:id>/check-availability/',CheckAvailability.as_view()),


    path('api/owner/<int:id>/newadmission/',AdmissionListAPI.as_view()),
    path('api/owner/<int:id>/newadmission/download/',AdmissionCSVAPI.as_view()),
    path('api/owner/<int:id>/newadmission/mail/',AdmissionCSVMailAPI.as_view()),

    path('api/owner/<int:id>/renewal/',RenewalListAPI.as_view()),
    path('api/owner/<int:id>/renewal/download/',RenewalCSVAPI.as_view()),
    path('api/owner/<int:id>/renewal/mail/',RenewalCSVMailAPI.as_view()),

    path('api/student/libraryoffer/',StudentLibraryOfferAPI.as_view()),

]