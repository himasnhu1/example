from django.urls import path, include
from .enquiryapi import *
from .views import *
from .ownerreports import * 
from .predictionapi import *
from .onwersubapi import *
from .ownergraphapi import *

urlpatterns = [
    path('api/studentenquiry/', EnquiryApi.as_view()),
    path('api/studentenquiry/followup/',EnquiryFollowApi.as_view(), name='Enquiry-follow-up'),
    #path('api/branch-owner/<int:id>/',BranchOwnerListAPI.as_view()),
    path('api/owner/<int:id>/employee/',BranchEmployeeListAPI.as_view()),
    path('api/owner/<int:id>/employee/<int:pk>/',BranchEmployeeUpdateAPI.as_view()),
    path('api/owner/details/<int:id>/',OwnerDetailAPI.as_view()),

    #dashboard graphs
    path('api/owner/extra-income/graph/',OwnerExtraIncomeGraphAPI.as_view()),  #ExtraIncome graph  1st graph
    path('api/owner/weekwise-profit/',WeekwiseProfitAPI.as_view()),            # Profit week wise (completed) #2nd graph
    # path('api/onwer-income-expense-graph/<int:id>/',OwnerGraphIncomeExpenseAPI.as_view()),   #kill it
    path('api/owner/income-expense-graph-filter/',OwnerGraphIncomeExpenseFilterAPI.as_view()),      #3rd graph 
    path('api/owner/monthly-activity/',OwnerActivityReportAPI.as_view()),  #4th graph  completed

    path('api/owner/monthly-expense/<int:id>/',OwnerExpenseMonthlyAPI.as_view()),    #monthly Expense
    path('api/owner/monthly-income/<int:id>/',OnwerMonthlyIncomeAPI.as_view()),      #montly Income

    path('api/owner/<int:id>/expense/',OwnerExpenseAPI.as_view()),   #for owner expense bottom button  #delete
    path('api/owner/<int:id>/expense/month/',OwnerMonthlyExpenseAPI.as_view()),          #delete

    
    path('api/owner-income-prediction/',PotentialRevenueMonthlyAPI.as_view()),
    path('api/owner/extra-income/',OwnerExtraIncomeAPI.as_view()),   ## UBF income all branches  #inner screen
    path('api/owner/extra-income/<int:id>/',OwnerExtraIncomeBranchAPI.as_view()),  ##UBF income branch wise
    path('api/owner/branch-weekwise-report/',WeekwiseIncomeExpenseAPI.as_view()),    ## changed  #weekwise graph
    path('api/owner/expense-graph/point/',MonthlyExpensePointAPI.as_view()),  #checked
    path('api/owner/income-graph/point/',MonthlyIncomePointAPI.as_view()),  #checked


    path('api/owner/student/pending-notification/<int:id>/',DueDateNotificationAPI.as_view()),  #bell

    # path('api/branch-feedbackcomplain/<int:id>/',FeedbackListAPI.as_view()),

    path('api/employee/<int:id>/dashboard/',OwnerEmployeeDashboardAPI.as_view()),   #checked
    path('api/verification-otp/',OTPEmailAPI.as_view()),
    
    path('api/owner/subscription/add/',OwnerSubAPI.as_view()),                     #checked
    path('api/owner/subscription/confirm-payment/',ConfirmPaymentAPI.as_view()),   #checked
    path('api/owner/subscription/view/',OwnerSubViewAPI.as_view()),                #checked
    path('api/owner/subscription-plans/',OwnerPlanView.as_view()),                 #checked


    path('api/owner/active-branches/',ActiveBranchAPI.as_view()),                  #checked

    path('api/owner/<int:id>/partner/',PartnerAPI.as_view()),                      #checked

    path('api/owner/<int:id>/library-holiday/',BranchHolidayAPI.as_view()),
    path('api/owner/<int:id>/library-holiday/<int:pk>/',BranchHolidayUpdateAPI.as_view()),

    path('api/owner/device-reg/',OwnerDeviceRegAPI.as_view()),                     #checked

    path('api/owner/<int:id>/student-dropdown/',StudentList.as_view()),            #checked

    path('api/owner/<int:id>/invoices/owner/',ManageInvoiceOwner.as_view()),
    path('api/owner/<int:id>/invoices/student/',ManageInvoiceStudent.as_view()),

]