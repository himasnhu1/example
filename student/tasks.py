from __future__ import absolute_import, unicode_literals
from celery.task.schedules import crontab
from celery.decorators import periodic_task
from celery import shared_task
from django.db.models import Q, Count
from .models import *
import datetime
from django.core.exceptions import ObjectDoesNotExist
from library import models as librarymodels

from django.core.mail import EmailMultiAlternatives
from django.template import Context
from django.template.loader import render_to_string
from django.utils.html import strip_tags


@shared_task
def subscription_checker():
    students = Student.objects.all()

    for student in students:
        
        if student.active_subscription is None:
            pass
        else:
            activeSub = PurchasedSubscription.objects.get(id=student.active_subscription.id)
            print(activeSub)

            if activeSub.due_date.day - datetime.datetime.today().day <0:
                activeSub.active = False
                
                locker = librarymodels.LibraryLocker.objects.get(id=activeSub.locker.id)
                locker.assigned_student = None
                locker.save()
                studentObj = Student.objects.get(id=student.id)
                studentObj.active_subscription = None
                studentObj.save()
                activeSub.save()


@shared_task
def Student_absent():
    today = datetime.datetime.today()
    currentTime = datetime.datetime.now().time()
    students =Student.objects.all()
    for student in students:

        if student.active_subscription is None:
            pass
        else:
            activeSub = PurchasedSubscription.objects.get(id=student.active_subscription.id)
            #print("celery 1")
            for slot in activeSub.timeslots.all().order_by('start'):
                if slot.end > currentTime:
                    pass
                else:
                    present = StudentAttendance.objects.filter(student=student,date=today,slot=slot,present=True)
                    absent = StudentAttendance.objects.filter(student=student,date=today,slot=slot,present=False)
                    if present.count()==0 and absent.count()==0:
                        ab = StudentAttendance.objects.create(student=student,date=today,slot=slot,present=False,branch=student.library_branch)
                        activeSub.hoursUtilized = activeSub.hoursUtilized + (datetime.timedelta(hours=(slot.end.hour - slot.start.hour), minutes=(slot.end.minute - slot.start.minute)))
                        activeSub.save()

@shared_task
def Usage():

    students =Student.objects.all()

    for student in students:
        if student.active_subscription is None:
            pass
        else:
            activeSub = PurchasedSubscription.objects.get(id=student.active_subscription.id)
            totalhrs = activeSub.days*activeSub.shift_timings

            if (totalhrs - activeSub.hoursRemain.seconds//3600 )/100 >=50:
                html_content = render_to_string('usage/usage50.html',{"hoursremain":activeSub.hoursRemain})
                text_content = strip_tags(html_content)
                email = EmailMultiAlternatives('SRMS Usage Alert', text_content,'testingserver.12307@gmail.com',[student.mail,"yashch1998@gmail.com"])
                email.attach_alternative(html_content, "text/html")

                email.send()
                activeSub.usage50 = True
                activeSub.save()

            if (totalhrs - activeSub.hoursRemain.seconds//3600 )/100 >=85:
                html_content = render_to_string('usage/usage85.html',{"hoursremain":activeSub.hoursRemain})
                text_content = strip_tags(html_content)
                email = EmailMultiAlternatives('SRMS Usage Alert', text_content,'testingserver.12307@gmail.com',[student.mail,"yashch1998@gmail.com"])
                email.attach_alternative(html_content, "text/html")

                email.send()
                activeSub.usage85 = True
                activeSub.save()



