from django.db import models
from django.contrib.auth.models import Permission
from django.db.models.signals import pre_save,post_save
import datetime
from django.dispatch import receiver

class Owner(models.Model):
    library = models.ForeignKey('library.Library', on_delete=models.PROTECT)
    user = models.OneToOneField('core.User', on_delete=models.PROTECT)
    name = models.CharField(max_length=128)
    image = models.ImageField(blank=True, null=True)
    dob = models.DateField()
    
    mobile = models.CharField(max_length=10)
    alternate_mobile = models.CharField(max_length=10, blank=True, null=True)
    email = models.EmailField()

    address = models.CharField(max_length=128)
    city = models.CharField(max_length=256)
    state = models.CharField(max_length=16)
    pincode = models.CharField(max_length=6)
    location = models.CharField(max_length=256)

    branches = models.ManyToManyField('library.LibraryBranch',blank=True)
    basicSetup = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    active_subscription = models.ForeignKey('owner.OwnerSubscriptionPlan',related_name='owner_sub',on_delete=models.PROTECT,null=True,blank=True)
    class Meta:
        permissions = (
            ('can_add_partner', 'Can Add Partner'),
        )

class UserLibraryPermissions(models.Model):
    user = models.ForeignKey('core.User', on_delete=models.PROTECT)
    library_branch = models.ForeignKey('library.LibraryBranch', on_delete=models.PROTECT)
    permissions = models.ManyToManyField('auth.Permission')

    class Meta:
        verbose_name_plural = 'Owner/Employee Library Permissions'
        permissions = (
            ('can_add_permissions', 'Can Add Permissions'),
            ('can_delete_permissions', 'Can Delete Permissions'),
        )

class Employee(models.Model):
    library = models.ForeignKey('library.Library', on_delete=models.PROTECT)
    user = models.OneToOneField('core.User', on_delete=models.PROTECT)
    name = models.CharField(max_length=128)
    image = models.ImageField(blank=True, null=True)
    dob = models.DateField()

    mobile = models.CharField(max_length=10)
    alternate_mobile = models.CharField(max_length=10, blank=True, null=True)
    email = models.EmailField()

    address = models.CharField(max_length=128)
    city = models.CharField(max_length=256)
    state = models.CharField(max_length=16)
    pincode = models.CharField(max_length=6)
    location = models.CharField(max_length=256)

    branches = models.ManyToManyField('library.LibraryBranch',blank=True)

    start_shift = models.TimeField()
    end_shift = models.TimeField()
    id_proof = models.ImageField(blank=True, null=True)
    active = models.BooleanField(default=True)

enquiry_choices = (
    ('Open', 'Open'),
    ('Registered', 'Registered'),
    ('Withdrawed', 'Withdrawed'),
)
class Enquiry(models.Model):
    library_branch = models.ForeignKey('library.LibraryBranch', on_delete=models.PROTECT)

    # student = models.ForeignKey('student.Student', on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    email = models.EmailField()
    mobile = models.CharField(max_length=10)
    exam_preparing_for = models.ManyToManyField('core.ExamsPreparingFor')

    preferred_joining_date = models.DateField()
    follow_up_date = models.DateField()
    preferred_shift_time = models.CharField(max_length=128)
    comment = models.TextField()
    status = models.CharField(max_length=10, choices=enquiry_choices, default='Open')
    date = models.DateField(auto_now_add=True)
    withdraw_reason = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Enquiries'

class EnquiryFollowUp(models.Model):
    enquiry = models.ForeignKey('owner.Enquiry', on_delete=models.CASCADE)
    title = models.CharField(max_length=128, blank=True, null=True)
    details = models.TextField()
    next_follow_up_date = models.DateField(null=True, blank=True)
    date = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Follow-Ups'

payment_mode_choices = (
    ('Cash', 'Cash'),
    ('Paytm', 'Paytm'),
    ('UPI', 'UPI'),
)
class Expense(models.Model):
    library_branch = models.ForeignKey('library.LibraryBranch', on_delete=models.PROTECT)
    date = models.DateField()
    title = models.CharField(max_length=128)
    amount_paid = models.PositiveSmallIntegerField()
    payment_mode = models.CharField(max_length=16, choices=payment_mode_choices)
    invoice = models.FileField(blank=True, null=True)
    note = models.TextField()

    class Meta:
        verbose_name_plural = 'Expenses'

feedback_choices = (
    ('Feedback', 'Feedback'),
    ('Complaint', 'Complaint'),
)
class Feedback(models.Model):
    library_branch = models.ForeignKey('library.LibraryBranch', on_delete=models.PROTECT)
    type = models.CharField(max_length=8, choices=feedback_choices)
    student = models.ForeignKey('student.Student', on_delete=models.PROTECT)
    title = models.CharField(max_length=128)
    details = models.TextField()
    date = models.DateField(auto_now_add=True)
    reponse = models.TextField(default="")
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Feedbacks/Complaints'

class FeedbackFollowUp(models.Model):
    feedback = models.ForeignKey('owner.Feedback', on_delete=models.PROTECT)
    detail = models.TextField()
    expense = models.ForeignKey('owner.Expense', on_delete=models.PROTECT, null=True, blank=True)
    date = models.DateField(auto_now_add=True)

class EmployeeFeedback(models.Model):
    library_branch = models.ForeignKey('library.LibraryBranch', on_delete=models.PROTECT)
    type = models.CharField(max_length=8, choices=feedback_choices)
    employee = models.ForeignKey('owner.Employee', on_delete=models.PROTECT)
    title = models.CharField(max_length=128)
    details = models.TextField()
    date = models.DateField(auto_now_add=True)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Employee Feedbacks/Complaints'

class EmployeeFeedbackFollowUp(models.Model):
    feedback = models.ForeignKey('owner.EmployeeFeedback', on_delete=models.PROTECT)
    detail = models.TextField()
    expense = models.ForeignKey('owner.Expense', on_delete=models.PROTECT, null=True, blank=True)
    date = models.DateField(auto_now_add=True)

class OwnerSubscriptionPlan(models.Model):
    owner = models.ForeignKey('owner.Owner',on_delete=models.PROTECT)
    title = models.CharField(max_length=50,blank=True,null=True)
    days = models.PositiveSmallIntegerField()
    startdate = models.DateField(auto_now_add=True)
    enddate = models.DateField(blank=True,null=True)
    branchesAllowed = models.PositiveSmallIntegerField()
    amount = models.PositiveSmallIntegerField()
    order_id = models.CharField(max_length=64,blank=True,null=True)
    purchased = models.BooleanField(default=False)
    activeBranch = models.ManyToManyField('library.LibraryBranch',blank=True)
    active= models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'Owner Subscription'
    
    def __str__(self):
        return self.owner.name

class Ownerpayment(models.Model):
    subscription = models.ForeignKey(OwnerSubscriptionPlan,on_delete=models.PROTECT)
    payment_id = models.CharField(max_length=100)
    amount_paid = models.PositiveIntegerField()

    paymentmode = models.CharField(max_length=50,default="Razor Pay")

    class Meta:
        verbose_name_plural = 'Owner Payment'

    def __str__(self):
        return self.subscription.owner.name

class OwnerDevice(models.Model):

    owner = models.ForeignKey(Owner,on_delete=models.PROTECT)
    registration_id = models.CharField(max_length=256,unique=True)

    class Meta:
        verbose_name_plural = 'Owner Devices'

    def __str__(self):
        return self.owner.name

class OwnerSubPlan(models.Model):

    plan_name = models.CharField(max_length=256)
    amount = models.PositiveIntegerField()
    extra= models.PositiveIntegerField()
    days= models.PositiveIntegerField()
    date = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Owner Subscription Plans'

    def __str__(self):
        return self.plan_name



# @receiver(post_save, sender=Owner)
# def add_owner_sub(sender, instance, created, *args, **kwargs):
#     if created:
        # sub = OwnerSubscriptionPlan.objects.create(owner = instance,title="Free Tier",days=45,branchesAllowed=2,amount=0,active=True)
        # sub.save()
        # instance.active_subscription = sub

@receiver(post_save, sender=OwnerSubscriptionPlan)
def prep_sub(sender, instance,created,*args, **kwargs):
    if created:
        instance.enddate = instance.startdate + datetime.timedelta(days=instance.days)

# @receiver(pre_save, sender=OwnerSubscription)
# def prep_sub(sender, instance,*args, **kwargs):
#     if instance._state.adding:
#         instance.enddate = instance.startdate + datetime.timedelta(days=instance.days)