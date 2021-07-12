from django.shortcuts import render
from . import models, serializers
from rest_framework import viewsets, status, permissions
from django.db.models import Q
import ast
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework.generics import *
from student import models as studentmodels
from core import models as coremodels
from owner import models as ownermodels
# Create your views here.
class LibraryAPIViewSet(viewsets.ModelViewSet):
    queryset = models.Library.objects.all()
    serializer_class = serializers.LibrarySerializer
    permission_classes = [permissions.IsAuthenticated, ]
    http_method_names = ['post','head','options']

    # def get_queryset(self):
    #     queryset = models.TimeSlot.objects.filter(active=True)
    #     return queryset
    #
    # def list(self, request, *args, **kwargs):
    #     user = request.user or request.auth
    #     serializer_context = {
    #         'request': request,
    #     }
    #     if user.is_admin:
    #         queryset = models.TimeSlot.objects.all()
    #         serializer = serializers.TimeSlotSerializer(queryset, many=True, context=serializer_context)
    #         return Response(serializer.data)
    #     else:
    #         queryset = models.TimeSlot.objects.filter(active=True)
    #         serializer = serializers.TimeSlotSerializer(queryset, many=True, context=serializer_context)
    #         return Response(serializer.data)
    #
    # def retrieve(self, request, pk=None, *args, **kwargs):
    #     serializer_context = {
    #         'request': request,
    #     }
    #     queryset = models.TimeSlot.objects.all()
    #     time_slot = get_object_or_404(queryset, pk=pk)
    #     serializer = serializers.TimeSlotSerializer(time_slot, context=serializer_context)
    #     return Response(serializer.data)
    #
    # def update(self, request, *args, **kwargs):
    #     partial = kwargs.pop('partial', False)
    #     instance = self.get_object()
    #     serializer = self.get_serializer(instance, data=request.data, partial=partial)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_update(serializer)
    #     return Response(serializer.data)
    #
    # def create(self, request, *args, **kwargs):

    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_create(serializer)
    #     headers = self.get_success_headers(serializer.data)
    #     return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    #
    # def destroy(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     self.perform_destroy(instance)
    #     return Response(status=status.HTTP_204_NO_CONTENT)
    #
    # def partial_update(self, request, *args, **kwargs):
    #     kwargs['partial'] = True
    #     return self.update(request, *args, **kwargs)
    #
    # def get_permissions(self):
    #     if self.action == 'list':
    #   +      permission_classes = [IsAuthenticated]
    #     else:
    #         permission_classes = [IsAdminUser]
    #     return [permission() for permission in permission_classes]


class LibraryBranchAPIViewSet(viewsets.ModelViewSet):
    queryset = models.LibraryBranch.objects.all()
    serializer_class = serializers.LibraryBranchSerializer
    permission_classes = [permissions.IsAuthenticated, ]
    http_method_names = ['post','head','options']

    def get_queryset(self):
        queryset = models.LibraryBranch.objects.all()

        library = self.request.query_params.get('library', None)
        if library is not None:
            queryset = queryset.filter(library_id = branch)

        search = self.request.query_params.get('search', None)
        if s+earch is not None:
            queryset = queryset.filter(name__icontains  =search)

        return queryset

    def create(self,request,*args,**kwargs):
        try:
            owner = ownermodels.Owner.objects.get(user=request.user)
        except ObjectDoesNotExist:
            return Response({"error":"User is not an owner"},status=400)
        if owner.active_subscription is None:
            return Response({"error":"No active Subscription"},status=400)
        try:
            ownersub = ownermodels.OwnerSubscriptionPlan.objects.get(id=owner.active_subscription.id)
        except ObjectDoesNotExist:
            return Response("No active Subscription",status=400)
        branches = self.queryset.filter(library=owner.library)
        if ownersub.branchesAllowed<=branches.count():
            return Response("Max library for subscription has reached",status=400)
        if 'source' in request.data:
            if 'opening_days' in request.data:
                request.data['opening_days'] =  ast.literal_eval(request.data['opening_days'])
            if 'ammenities' in request.data:    
                request.data['ammenities'] =  ast.literal_eval(request.data['ammenities'])
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        library=self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        if 'no_of_lockers' in request.data:
            for i in range(1,int(request.data["no_of_lockers"])+1):
                locker = models.LibraryLocker.objects.create(library_branch_id=serializer.data["id"],locker_number = 'Locker '+str(i),active=True)
        if branches.count()==1:
            owner.basicSetup = True
            owner.save()
        branch = self.queryset.get(id=serializer.data["id"])
        ownersub.activeBranch.add(branch)
        ownersub.save()
        owner.branches.add(branch)
        owner.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class LibraryLockerAPIViewSet(viewsets.ModelViewSet):
    queryset = models.LibraryLocker.objects.all()
    serializer_class = serializers.LibraryLockerSerializer
    permission_classes = [permissions.IsAuthenticated, ]
    http_method_names = []

    def get_queryset(self):
        queryset = models.LibraryLocker.objects.all()

        branch = self.request.query_params.get('branch', None)
        if branch is not None:
            queryset = queryset.filter(library_branch_id = branch)

        active = self.request.query_params.get('active', None)
        if active is not None:
            queryset = queryset.filter(active  = active)

        available = self.request.query_params.get('available', None)
        if available is not None:
            queryset = queryset.filter(assigned_student__isnull=True)

        return queryset

class HolidaysAPIViewSet(viewsets.ModelViewSet):
    queryset = models.Holidays.objects.all()
    serializer_class = serializers.HolidaysSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def get_queryset(self):
        queryset = models.Holidays.objects.all()

        branch = self.request.query_params.get('branch', None)
        if branch is not None:
            queryset = queryset.filter(library_branch_id = branch)

        month = self.request.query_params.get('month', None)
        if month is not None:
            queryset = queryset.filter(start__month = month)

        year = self.request.query_params.get('year', None)
        if year is not None:
            queryset = queryset.filter(start__year = year)

        from_date = self.request.query_params.get('from_Date', None)
        if from_date is not None:
            from_date = datetime.datetime.strptime(from_date, "%Y-%m-%d").date()
            queryset = queryset.filter(start__gte = from_date)

        to_date = self.request.query_params.get('to_date', None)
        if to_date is not None:
            to_date = datetime.datetime.strptime(to_date, "%Y-%m-%d").date()
            queryset = queryset.filter(end__lte = to_date)

        search = self.request.query_params.get('search', None)
        if search is not None:
            queryset = queryset.filter(Q(title__icontains  =search) | Q(details__icontains  =search))

        queryset = queryset.order_by('-start')
        return queryset

    def create(self,request,*args,**kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        students = studentmodels.Student.objects.filter(library_branch=request.data["library_branch"])
        for student in students:
            title = "New Holiday has been added on : "+str(request.data["start"])+str(request.data['title'])
            description = "Holiday has been added \n"+str(request.data["details"])
            notiftype = "holiday"

            notif = coremodels.Notifications.objects.create(student=student,title=title,description=description,notifType=notiftype)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)        

class LibrarySubscriptionViewSet(viewsets.ModelViewSet):
    queryset = models.LibrarySubscription.objects.all()
    serializer_class = serializers.LibrarySubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def get_queryset(self):
        queryset = models.LibrarySubscription.objects.all()

        branch = self.request.query_params.get('branch', None)
        if branch is not None:
            queryset = queryset.filter(library_branch_id = branch)

        no_of_hours = self.request.query_params.get('no_of_hours', None)
        if no_of_hours is not None:
            queryset = queryset.filter(no_of_hours = int(no_of_hours))

        return queryset


class LibraryOfferViewSet(viewsets.ModelViewSet):
    queryset = models.LibraryOffer.objects.all()
    serializer_class = serializers.LibraryOfferSerializer
    permission_classes = [permissions.IsAuthenticated, ]
    http_method_names = ['post','option','head']
    
    def create(self,request,*args,**kwargs):

        if not request.user.is_owner and not request.user.is_employee:
            return Response({"Error":"User is not an Owner/Employee"})
        
        if request.user.is_owner:
            instance = ownermodels.Owner.objects.get(user=request.user)
        
        elif request.user.is_employee:
            instance = ownermodels.Employee.objects.get(user=request.user)

        branchlist = instance.branches.all()
        if int(request.data["library"]) not in branchlist.values_list('id', flat=True):
            return Response({"Error":"Branch does not belong to this owner"},status=403)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)       

class QrCodeViewSet(viewsets.ModelViewSet):
    queryset = models.AttendanceQrCode.objects.all()
    serializer_class = serializers.QrcodeSerializer
    permission_classes = [permissions.IsAuthenticated, ]
    http_method_names = ['post','options','head']

    def create(self,request,*args,**kwargs):
        if not request.user.is_owner:
            return Response({"Error":"User is not an Owner"})
        
        instance = ownermodels.Owner.objects.get(user=request.user)

        branchlist = instance.branches.all()
        if int(request.data["branch"]) not in branchlist.values_list('id', flat=True):
            return Response({"Error":"Branch does not belong to this owner"},status=403)

        queryset = self.queryset.all()
        try:
            currentActive = queryset.get(branch = request.data["branch"],active=True)
        except ObjectDoesNotExist:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except:
            return Response("Some Internal Error", status=400)
        
        currentActive.active = False
        currentActive.save()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class LibraryBranchListAPI(ListAPIView):
    queryset = models.LibraryBranch.objects.all()
    serializer_class = serializers.MinLibraryBranchSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def list(self,request,*args,**kwargs):
        #print()
        if not request.user.is_owner and not request.user.is_employee:
            return Response({"Error":"User is not an owner/employee"},status=403)
        
        owner = ownermodels.Owner.objects.get(user=request.user)

        queryset = models.LibraryBranch.objects.none()
        for i in owner.branches.all():

            queryset = self.queryset.filter(id=i.id) | queryset

        search = request.query_params.get('search',None)
        if search is not None:
            queryset = queryset.filter(name__icontains=search)

        serializer = self.serializer_class(queryset,many=True)

        return Response(serializer.data,status=200)
    
class LibraryBranchLockerListAPI(ListAPIView):
    queryset = models.LibraryLocker.objects.all()
    serializer_class = serializers.MinLibraryLockerSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def get_queryset(self):
        queryset = self.queryset.filter(library_branch=self.kwargs["id"])

        booked = self.request.query_params.get('booked', None)
        if booked is not None:
            if booked=="true":
                queryset = queryset.filter(assigned_student__isnull=False)
            else:
                queryset = queryset.filter(assigned_student__isnull=True)

        active = self.request.query_params.get('active', None)
        if active is not None:
            if active=="true":
                queryset = queryset.filter(active=True)
            else:
                queryset = queryset.filter(active=False)

        return queryset

class LibraryBranchSubListAPI(ListAPIView):

    queryset = models.LibrarySubscription.objects.all()
    serializer_class = serializers.LibrarySubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def get_queryset(self):
        queryset = self.queryset.filter(library_branch = self.kwargs["id"])

        return queryset

class OwnerSwitchBranchAPI(ListAPIView):

    queryset = models.LibraryBranch.objects.all()
    serializer_class = serializers.BranchSwitchSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    # def get_queryset(self):

    #     queryset = self.queryset.filter(library = self.kwargs["id"])

    #     return queryset    

    def list(self,request,*args,**kwargs):
        if not request.user.is_owner:
            return Response({"Error":"User is not an owner"},status=403)
        
        owner = ownermodels.Owner.objects.get(user=request.user)

        queryset = models.LibraryBranch.objects.none()
        for i in owner.branches.all():

            queryset = self.queryset.filter(id=i.id) | queryset
        
        serializer = self.serializer_class(queryset,many=True)

        data=[{
            "id":"all",
            "name":"all",
        }]
        for i in serializer.data:
            data.append(i)

        return Response(data,status=200)