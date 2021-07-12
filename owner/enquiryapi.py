from django.shortcuts import render

from rest_framework import viewsets, status, permissions
import datetime
from rest_framework.decorators import action
from django.db.models import Q
from rest_framework.response import Response
from core.models import *
from core.serializers import *

from owner.models import *
from owner.serializers import *

from rest_framework.generics import *

class EnquiryApi(ListAPIView,CreateAPIView,UpdateAPIView):

    queryset = Enquiry.objects.all()
    serializer_class = EnquirySerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def get_queryset(self):
        
        queryset = self.queryset.filter(library_branch=self.request.data["library_branch"])
        active = self.request.query_params.get('status', None)
        if status is not None:
            if status=="open":
                queryset = queryset.filter(status="Open")
            elif status=="closed":
                queryset = queryset.filter(Q(status="Registered")|Q(status="Withdrawed"))

        from_date = self.request.query_params.get('from_Date', None)

        if from_date is not None:
            from_date = datetime.datetime.strptime(from_date, "%Y-%m-%d").date()
            queryset = queryset.filter(add_date__gte = from_date)

        to_date = self.request.query_params.get('to_date', None)
        if to_date is not None:
            to_date = datetime.datetime.strptime(to_date, "%Y-%m-%d").date()
            queryset = queryset.filter(add_date__lte = to_date)
        
        search = self.request.query_params.get('search', None)
        if search is not None:
            queryset = queryset.filter(name__icontains  =search)

        return queryset

    def partial_update(self,request,*args,**kwargs):

        enquiry = self.queryset.get(id=request.data["id"])
        serializer = self.serializer_class(enquiry,data=request.data,partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,status=200)

class EnquiryFollowApi(CreateAPIView):

    queryset = EnquiryFollowUp.objects.all()
    serializer_class = EnquiryFollowUpSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def create(self,request,*args,**kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        enquiry = Enquiry.objects.get(id=request.data["enquiry"])
        data ={
            "follow_up_date": request.data["next_follow_up_date"]
        }
        serializer2 = EnquirySerializer(enquiry,data=data,partial=True)
        serializer2.is_valid(raise_exception=True)
        #enquiry.follow_up_date = datetime.datetime.strptime(request.data["next_follow_up_date"], "%Y-%m-%d").date()
        serializer2.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)




