from django.urls import path, include
from .enquiryapi import *
from .views import *
from .ownerreports import * 
from .predictionapi import *
from .onwersubapi import *
from .employeeapi import *

urlpatterns = [
    
    path('api/employee/<int:id>/enquiry/',EmployeeEnquiryApi.as_view()),
    path('api/employee/<int:id>/enquiry/<int:pk>',EmployeeEnquiryUpdateApi.as_view()),
    path('api/employee/<int:id>/enquiry/followup/',EmployeeEnquiryFollowApi.as_view()),

    path('api/employee/<int:id>/feedback/',EmployeeFeedbackListAPI.as_view()),              #checked
    path('api/employee/<int:id>/feedback/<int:pk>/',EmployeeFeedbackUpdateAPI.as_view()),   #checked
    
    path('api/employee/<int:id>/expense/',EmployeeExpenseAPI.as_view()),                    #checked
    path('api/employee/<int:id>/expense/month/',EmployeeMonthlyExpenseAPI.as_view()),       #checked

    path('api/employee/<int:id>/pending/',StudentPendingsAPI.as_view()),                    #checked
    path('api/employee/<int:id>/pending-count/',StudentPendingCountAPI.as_view()),          #checked

]