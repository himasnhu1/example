from __future__ import absolute_import, unicode_literals
from celery.task.schedules import crontab
from celery.decorators import periodic_task
from celery import shared_task
from django.db.models import Q, Count,Sum
from .models import *
import datetime
from django.core.exceptions import ObjectDoesNotExist
from student.models import Student,PurchasedSubscription,StudentPayment
import datetime

@shared_task
def Notification_centre():
    students = Student.objects.all()
    today = datetime.date.today()
    for student in students:
        
        if student.active_subscription is None:
            pass
        else:
            activeSub = PurchasedSubscription.objects.get(id=student.active_subscription.id)

            if activeSub.due_date.day > today.day:
                if activeSub.due_date.day-today.day<6:

                    payments = StudentPayment.objects.filter(purchased_subscription=activeSub).aggregate(Sum('amount_paid'))
                    payments = payments['amount_paid__sum']
                    if payments:
                        due = activeSub.total_amount - payments
                    else:
                        due = activeSub.total_amount
                    if due>0:
                        
                        title = "Subscription due fees : Rs. "+str(due)+' pending. \n Please clear the dues before subscription ends \n\n Days remaining'+str(activeSub.due_date.day-today.day)
                        description = "Subscription due fees : Rs. "+str(due)+' pending. \n Please clear the dues before subscription ends \n\n Days remaining'+str(activeSub.due_date.day-today.day)+"\n Please Clear teh dues fees and dont forget to Renew your subscription to continue enjoying the library service."
                        notiftype = "Subscription Due Fees"

                        notif = Notifications.objects.create(student=student,title=title,description=description,notifType=notiftype)

                    title = "Subscription due date coming in : "+str(activeSub.due_date.day-today.day)+' days\n Please Renew your subscription'
                    description = "Subscription getting dued in " +str(activeSub.due_date.day-today.day)+" days\n Please Renew the subscription to continue enjoying the library service."
                    notiftype = "Subscription Due Date"

                    notif = Notifications.objects.create(student=student,title=title,description=description,notifType=notiftype)
                
            else:
                days_left =(datetime.date(activeSub.due_date.year, activeSub.due_date.month, 1) - datetime.date(today.year, today.month, 1)).days
                if days_left<6:
                    payments = StudentPayment.objects.filter(purchased_subscription=activeSub).aggregate(Sum('amount_paid'))
                    payments = payments['amount_paid__sum']
                    if payments:
                        due = activeSub.total_amount - payments
                    else:
                        due = activeSub.total_amount

                    if due > 0:
                        title = "Subscription due fees : Rs. "+str(due)+' pending. \n Please clear the dues before subscription ends \n\n Days remaining'+str(days_left)
                        description = "Subscription due fees : Rs. "+str(due)+' pending. \n Please clear the dues before subscription ends \n\n Days remaining'+str(days_left)+"\n Please Clear teh dues fees and dont forget to Renew your subscription to continue enjoying the library service."
                        notiftype = "Subscription Due Fees"

                        notif = Notifications.objects.create(student=student,title=title,description=description,notifType=notiftype)
                    
                    title = "Subscription due date coming in : "+str(days_left)+'\n Please Renew your subscription'
                    description = "Subscription getting due in " +str(days_left)+"\n Please Renew the subscription to continue enjoying the library service."
                    notiftype = "Subscription Due Date"

                    notif = Notifications.objects.create(student=student,title=title,description=description,notifType=notiftype)

