from rest_framework import routers
from core import views as coreviews
from library import views as libraryviews
from owner import views as ownerviews
from student import views as studentviews
from student.studentcornerapi import *
from django.urls import path, include
router = routers.DefaultRouter()

# core routers

router.register('users', coreviews.UserSerializerAPIViewSet, basename='user')
#router.register('fcm',coreviews.DeviceViewSet, basename='fcm')
router.register('higher-education', coreviews.HigherEducationAPIViewSet, basename='highereducation')
router.register('exams-preparing-for', coreviews.ExamsPreparingForAPIViewSet, basename='examspreparingfor')
router.register('opening-days', coreviews.OpeningDaysAPIViewSet, basename='openingdays')
router.register('time-slot', coreviews.TimeSlotAPIViewSet, basename='timeslot')

router.register('incidents', coreviews.IncidentAPIViewSet, basename='incident')
router.register('faqs', coreviews.FAQAPIViewSet, basename='faq')
#router.register('notification', coreviews.NotificationAPIViewSet, basename='notification')
router.register('current-affairs-category', coreviews.CurrentAffairCategoryAPIViewSet, basename='currentaffaircategory')
router.register('current-affairs', coreviews.CurrentAffairAPIViewSet, basename='currentaffair')
router.register('current-affairs-images', coreviews.CurrentAffairImageAPIViewSet, basename='currentaffairimage')
router.register('ammenities', coreviews.AmmenitiesAPIViewSet, basename='ammenity')

# Library routers
router.register('library', libraryviews.LibraryAPIViewSet, basename='library')
router.register('library-branch', libraryviews.LibraryBranchAPIViewSet, basename='librarybranch')
#router.register('library-locker', libraryviews.LibraryLockerAPIViewSet, basename='librarylocker')
router.register('library-subscriptions', libraryviews.LibrarySubscriptionViewSet, basename='librarysubscription')
router.register('holidays', libraryviews.HolidaysAPIViewSet, basename='holidays')
router.register('library-offers', libraryviews.LibraryOfferViewSet, basename='libraryoffer')
router.register('library-qrcode', libraryviews.QrCodeViewSet, basename='libraryqrcode')



# Owner routers
router.register('owners', ownerviews.OwnerAPIViewSet, basename='owner')
router.register('user-library-permissions', ownerviews.UserLibraryPermissionsAPIViewSet, basename='userlibrarypermissions')
#router.register('employees', ownerviews.EmployeeAPIViewSet, basename='employee')
router.register('enquiry', ownerviews.EnquiryAPIViewSet, basename='enquiry')
router.register('enquiry-follow-up', ownerviews.EnquiryFollowUpAPIViewSet, basename='enquiryfollowup')
router.register('expense', ownerviews.ExpenseAPIViewSet, basename='expense')
router.register('library-feedback', ownerviews.FeedbackAPIViewSet, basename='libraryfeedback')
router.register('library-feedback-follow-up', ownerviews.FeedbackFollowUpAPIViewSet, basename='feedbackfollowup')
router.register('employee-library-feedback', ownerviews.EmployeeFeedbackAPIViewSet, basename='employeelibraryfeedback')
router.register('employee-library-feedback-follow-up', ownerviews.EmployeeFeedbackFollowUpAPIViewSet, basename='employeefeedbackfollowup')


# Student routers

router.register('students', studentviews.StudentAPIViewSet, basename='student')
router.register('student-attendance', studentviews.StudentAttendanceAPIViewSet, basename='studentattendance')
router.register('student-purchased-subscriptions', studentviews.PurchasedSubscriptionAPIViewSet, basename='purchasedsubscription')
router.register('student-payments', studentviews.StudentPaymentAPIViewSet, basename='studentpayment')
#router.register('studentcorner', StudentAPIViewSet, basename='studentcorner')
#router.register('studentcorner',studentviews.StudentCornerAPI,basename='studentcorner')

# urlpatterns = [
#     path('', include("student.urls")),
# ]
