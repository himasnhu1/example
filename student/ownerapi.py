from django.shortcuts import render
from . import models, serializers
from rest_framework import viewsets, status, permissions
import datetime
from rest_framework.decorators import action
from django.db.models import Q
from rest_framework.response import Response

from django.http import HttpResponse
from library import models as librarymodels
from owner import models as ownermodels
from django.core.exceptions import ObjectDoesNotExist

from core import models as coremodels
from core import serializers as coreserializers
from rest_framework.views import APIView

from rest_framework.generics import *
import ast
import csv

from django.core.mail import EmailMessage
from io import StringIO

from django.core.mail import EmailMultiAlternatives
from django.template import Context
from django.template.loader import render_to_string
from django.utils.html import strip_tags

class CheckAvailability(APIView):
    queryset = models.Student.objects.all()

    def get(self,request,id):
        queryset = self.queryset.filter(library_branch=id,active_subscription__isnull=False)

        branch = librarymodels.LibraryBranch.objects.get(id=id)
        seats = branch.seat_capacity
        from_date = self.request.query_params.get('from_date', None)
        to_date = self.request.query_params.get('to_date', None)
        if from_date is not None and to_date is not None:
            from_date = datetime.datetime.strptime(from_date, "%Y-%m-%d").date()
            #from_date = datetime.datetime.strptime(from_date, "%Y-%m-%d").date()
            queryset = queryset.filter(Q(active_subscription__due_date__gte=from_date) or Q(active_subscription__due_date__lte=to_date))
        elif from_date is not None:
            from_date = datetime.datetime.strptime(from_date, "%Y-%m-%d").date()
            queryset = queryset.filter(active_subscription__due_date__gte=from_date)

        elif to_date is not None:
            to_date = datetime.datetime.strptime(to_date, "%Y-%m-%d").date()
            queryset = queryset.filter(active_subscription__due_date__lte=to_date)

        from_time = self.request.query_params.get('from_time', None)
        to_time = self.request.query_params.get('to_time', None)
        if to_time is not None and from_time is not None:

            from_time=datetime.datetime.strptime(from_time, "%H:%M:%S").time()
            to_time=datetime.datetime.strptime(to_time, "%H:%M:%S").time()

            queryset = queryset.filter(active_subscription__timeslots__in=(coremodels.TimeSlot.objects.filter(start__gte=from_time,end__lte=to_time))).distinct()

        lockers = librarymodels.LibraryLocker.objects.filter(library_branch=id,assigned_student__isnull=True)
        students = []
        for student in self.queryset.all():
            attendance = models.StudentAttendance.objects.filter(student=student).order_by('-date')
            dt = datetime.date.today() - datetime.timedelta(7)
            if attendance.exists():
                last_attendance = attendance[0]
                if last_attendance.date < dt:
                    students.append(student)
        data={
            "available":(seats-queryset.count()),
            "lockers":lockers.count(),
            "absent for 7 days":len(students)
        }
        return Response(data,status=200)

class AdmissionListAPI(APIView):
    queryset = models.Student.objects.all()
    permission_classes = [permissions.IsAuthenticated, ]

    def get(self,request):
        today = datetime.date.today()
        try:
            owner = ownermodels.Owner.objects.get(user=request.user)
        except ObjectDoesNotExist:
            return Response({"error":"User is not an owner"},status=400)
        

        queryset = self.queryset.filter(library_branch=self.kwargs["id"]).order_by("-id")
        data=[]
        from_date = self.request.query_params.get('from_Date', None)

        for student in queryset:
            sub = models.PurchasedSubscription.objects.filter(student=student)
            from_date = self.request.query_params.get('from_date', None)
            if from_date is not None:
                from_date = datetime.datetime.strptime(from_date, "%Y-%m-%d").date()
                sub = sub.filter(date__gte = from_date)

            to_date = self.request.query_params.get('to_date', None)
            if to_date is not None:
                to_date = datetime.datetime.strptime(to_date, "%Y-%m-%d").date()
                sub = sub.filter(date__lte = to_date)
            # past = self.request.query_params.get('past', None)
            # if past is not None:
            #     if past=="days":
            #         days = 10
            #         if today.day <10:

            if sub.count()>0:
                sub = sub.order_by("id")
                timeslots = sub[0].timeslots.all()
                serializer = coreserializers.TimeSlotSerializer(timeslots,many=True)
                
                try:
                    image=student.image.url
                except:
                    image=""
                data.append(
                    {
                        "id":student.id,
                        "name":student.name,
                        "image":image,
                        "timeslot":serializer.data
                    })
        return Response(instance,status=200)

class AdmissionCSVAPI(APIView):
    queryset = models.Student.objects.all()
    permission_classes = [permissions.IsAuthenticated, ]

    def get(self,request,id):
        today = datetime.date.today()
        try:
            owner = ownermodels.Owner.objects.get(user=request.user)
        except ObjectDoesNotExist:
            return Response({"error":"User is not an owner"},status=400)

        queryset = self.queryset.filter(library_branch=self.kwargs["id"]).order_by("-id")

        data=[]
        for student in queryset:
            sub = models.PurchasedSubscription.objects.filter(student=student)
            from_date = self.request.query_params.get('from_date', None)
            if from_date is not None:
                from_date = datetime.datetime.strptime(from_date, "%Y-%m-%d").date()
                sub = sub.filter(date__gte = from_date)

            to_date = self.request.query_params.get('to_date', None)
            if to_date is not None:
                to_date = datetime.datetime.strptime(to_date, "%Y-%m-%d").date()
                sub = sub.filter(date__lte = to_date)
            
            if sub.count()>0:
                slots=[]
                sub = sub.order_by("id")
                timeslots = sub[0].timeslots.all()
                for slot in timeslots:
                    slots.append({
                        "start":str(slot.start),
                        "end":str(slot.end)
                    })              
                try:
                    image=student.image.url
                except:
                    image=""
                data.append(
                    {
                        "id":student.id,
                        "name":student.name,
                        "timeslot":slots
                    })

        response = HttpResponse(content_type='text/csv')  
        response['Content-Disposition'] = 'attachment; filename="file.csv"'  
        writer = csv.DictWriter(response,fieldnames=data[0].keys)
        writer.writeheader()
        for i in data:  
            writer.writerow(i)  
        return response

class AdmissionCSVMailAPI(APIView):
    queryset = models.Student.objects.all()
    permission_classes = [permissions.IsAuthenticated, ]

    def get(self,request,id):
        today = datetime.date.today()
        try:
            owner = ownermodels.Owner.objects.get(user=request.user)
        except ObjectDoesNotExist:
            return Response({"error":"User is not an owner"},status=400)

        queryset = self.queryset.filter(library_branch=self.kwargs["id"]).order_by("-id")

        data=[]
        for student in queryset:
            sub = models.PurchasedSubscription.objects.filter(student=student)
            from_date = self.request.query_params.get('from_date', None)
            if from_date is not None:
                from_date = datetime.datetime.strptime(from_date, "%Y-%m-%d").date()
                sub = sub.filter(date__gte = from_date)

            to_date = self.request.query_params.get('to_date', None)
            if to_date is not None:
                to_date = datetime.datetime.strptime(to_date, "%Y-%m-%d").date()
                sub = sub.filter(date__lte = to_date)
            
            if sub.count()>0:
                slots=[]
                sub = sub.order_by("id")
                timeslots = sub[0].timeslots.all()
                for slot in timeslots:
                    slots.append({
                        "start":str(slot.start),
                        "end":str(slot.end)
                    })              
                try:
                    image=student.image.url
                except:
                    image=""
                data.append(
                    {
                        "id":student.id,
                        "name":student.name,
                        "timeslot":slots
                    })

        csvfile = StringIO()
        fieldnames = list(data[0].keys())
        writer = csv.DictWriter(csvfile,fieldnames=fieldnames)
        writer.writeheader()
        for i in data:  
            writer.writerow(i)  
        html_content = render_to_string('owner/admissionreport.html')
        text_content = strip_tags(html_content)
        email = EmailMultiAlternatives('Admission Report', text_content,'testingserver.12307@gmail.com',[owner.email,'yashvikaschodancar@power2create.in',])
        email.attach_alternative(html_content, "text/html")
        
        email.attach('file.csv', csvfile.getvalue(), 'text/csv')
        email.send()
        return Response("Email Sent Successfully",status=200)


class RenewalListAPI(APIView):
    queryset = models.Student.objects.all()
    permission_classes = [permissions.IsAuthenticated, ]

    def get(self,request):
        today = datetime.date.today()
        try:
            owner = ownermodels.Owner.objects.get(user=request.user)
        except ObjectDoesNotExist:
            return Response({"error":"User is not an owner"},status=400)
        
        queryset = self.queryset.filter(library_branch=self.kwargs["id"]).order_by("-id")
        
        data = []

        for student in queryset:
            sub = models.PurchasedSubscription.objects.filter(student=student)
            from_date = self.request.query_params.get('from_date', None)
            if from_date is not None:
                from_date = datetime.datetime.strptime(from_date, "%Y-%m-%d").date()
                sub = sub.filter(date__gte = from_date)

            to_date = self.request.query_params.get('to_date', None)
            if to_date is not None:
                to_date = datetime.datetime.strptime(to_date, "%Y-%m-%d").date()
                sub = sub.filter(date__lte = to_date)
            # past = self.request.query_params.get('past', None)
            # if past is not None:
            #     if past=="days":
            #         days = 10
            #         if today.day <10:

            if sub.count()>1:
                sub = sub.order_by("id")
                timeslots = sub[0].timeslots.all()
                serializer = coreserializers.TimeSlotSerializer(timeslots,many=True)
                
                try:
                    image=student.image.url
                except:
                    image=""
                data.append(
                    {
                        "id":student.id,
                        "name":student.name,
                        "image":image,
                        "timeslot":serializer.data
                    })

        return Response(instance,status=200)

class RenewalCSVAPI(APIView):
    queryset = models.Student.objects.all()
    permission_classes = [permissions.IsAuthenticated, ]

    def get(self,request,id):
        today = datetime.date.today()
        try:
            owner = ownermodels.Owner.objects.get(user=request.user)
        except ObjectDoesNotExist:
            return Response({"error":"User is not an owner"},status=400)
        
        queryset = self.queryset.filter(library_branch=self.kwargs["id"]).order_by("-id")

        data=[]
        for student in queryset:
            sub = models.PurchasedSubscription.objects.filter(student=student)
            from_date = self.request.query_params.get('from_date', None)
            if from_date is not None:
                from_date = datetime.datetime.strptime(from_date, "%Y-%m-%d").date()
                sub = sub.filter(date__gte = from_date)

            to_date = self.request.query_params.get('to_date', None)
            if to_date is not None:
                to_date = datetime.datetime.strptime(to_date, "%Y-%m-%d").date()
                sub = sub.filter(date__lte = to_date)
            
            if sub.count()>1:
                slots=[]
                sub = sub.order_by("id")
                timeslots = sub[0].timeslots.all()
                for slot in timeslots:
                    slots.append({
                        "start":str(slot.start),
                        "end":str(slot.end)
                    })              
                try:
                    image=student.image.url
                except:
                    image=""
                data.append(
                    {
                        "id":student.id,
                        "name":student.name,
                        "timeslot":slots
                    })

        response = HttpResponse(content_type='text/csv')  
        response['Content-Disposition'] = 'attachment; filename="file.csv"'  
        writer = csv.DictWriter(response,fieldnames=data[0].keys)
        writer.writeheader()
        for i in data:  
            writer.writerow(i)  
        return response

class RenewalCSVMailAPI(APIView):
    queryset = models.Student.objects.all()
    permission_classes = [permissions.IsAuthenticated, ]

    def get(self,request,id):
        today = datetime.date.today()
        try:
            owner = ownermodels.Owner.objects.get(user=request.user)
        except ObjectDoesNotExist:
            return Response({"error":"User is not an owner"},status=400)
        
        queryset = self.queryset.filter(library_branch=self.kwargs["id"]).order_by("-id")

        data=[]
        for student in queryset:
            sub = models.PurchasedSubscription.objects.filter(student=student)
            from_date = self.request.query_params.get('from_date', None)
            if from_date is not None:
                from_date = datetime.datetime.strptime(from_date, "%Y-%m-%d").date()
                sub = sub.filter(date__gte = from_date)

            to_date = self.request.query_params.get('to_date', None)
            if to_date is not None:
                to_date = datetime.datetime.strptime(to_date, "%Y-%m-%d").date()
                sub = sub.filter(date__lte = to_date)
            
            if sub.count()>1:
                slots=[]
                sub = sub.order_by("id")
                timeslots = sub[0].timeslots.all()
                for slot in timeslots:
                    slots.append({
                        "start":str(slot.start),
                        "end":str(slot.end)
                    })              
                try:
                    image=student.image.url
                except:
                    image=""
                data.append(
                    {
                        "id":student.id,
                        "name":student.name,
                        "timeslot":slots
                    })

        csvfile = StringIO()
        fieldnames = list(data[0].keys())
        writer = csv.DictWriter(csvfile,fieldnames=fieldnames)
        writer.writeheader()
        for i in data:  
            writer.writerow(i)  
        html_content = render_to_string('owner/admissionreport.html')
        text_content = strip_tags(html_content)
        email = EmailMultiAlternatives('Renewal Report', text_content,'testingserver.12307@gmail.com',[owner.email,'yashvikaschodancar@power2create.in',])
        email.attach_alternative(html_content, "text/html")
        
        email.attach('file.csv', csvfile.getvalue(), 'text/csv')
        email.send()
        return Response("Email Sent Successfully",status=200)