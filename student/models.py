from django.db import models
import datetime
from django.db.models.signals import pre_save,post_save
from django.dispatch import receiver
from ubfcore import models as ubfmodels
from core import models as coremodels
import uuid
from reward import models as rewardmodels

gender_choices = (
    ('Male', 'Male'),
    ('Female', 'Female'),
    ('Not Specified','Not Specified')
)

class Student(models.Model):
    user = models.OneToOneField('core.User', on_delete=models.PROTECT)
    library_branch = models.ForeignKey('library.LibraryBranch', on_delete=models.PROTECT)

    name = models.CharField(max_length=128)
    image = models.ImageField(blank=True, null=True)
    gender = models.CharField(max_length=20, choices=gender_choices)
    dob = models.DateField()
    referral_code = models.CharField(max_length=8)

    mobile = models.CharField(max_length=10)
    alternate_mobile = models.CharField(max_length=10, blank=True, null=True)
    email = models.EmailField()

    address = models.CharField(max_length=128)
    city = models.CharField(max_length=256)
    state = models.CharField(max_length=16)
    pincode = models.CharField(max_length=6)
    location = models.CharField(max_length=256)

    higher_education = models.ForeignKey('core.HigherEducation', on_delete=models.PROTECT)
    exam_preparing_for = models.ManyToManyField('core.ExamsPreparingFor')

    id_proof_front = models.ImageField(blank=True, null=True)
    id_proof_rear = models.ImageField(blank=True, null=True)

    driving_proof_front = models.ImageField(blank=True, null=True)
    driving_proof_rear = models.ImageField(blank=True, null=True)

    voter_proof_front = models.ImageField(blank=True, null=True)
    voter_proof_rear = models.ImageField(blank=True, null=True)

    passport_proof_front = models.ImageField(blank=True, null=True)
    passport_proof_rear = models.ImageField(blank=True, null=True)

    college_proof_front = models.ImageField(blank=True, null=True)
    college_proof_rear = models.ImageField(blank=True, null=True)

    verified = models.BooleanField(default=False)
    add_date = models.DateField(auto_now_add=True)
    active_subscription = models.ForeignKey('student.PurchasedSubscription', on_delete=models.PROTECT, null=True, blank=True, related_name='active_subscription')

    def __str__(self):
        return self.name

class StudentAttendance(models.Model):
    branch = models.ForeignKey('library.LibraryBranch', on_delete=models.PROTECT)
    student = models.ForeignKey('student.Student', on_delete=models.PROTECT)
    date = models.DateField()
    in_time = models.TimeField(null=True, blank=True)
    out_time = models.TimeField(null=True, blank=True)
    note = models.TextField(blank=True, null=True)
    present = models.BooleanField(default=True)
    slot = models.ForeignKey('core.TimeSlot',on_delete = models.PROTECT,blank=True, null=True)


    def __str__(self):
        return str(self.student) + str(self.date)

    class Meta:
        permissions = (
            ('can_manage_off_time_students', 'Can Manage Off-Time Students'),
        )

class StudentOfftime(models.Model):

    #attendance =models.ForeignKey('StudentAttendance', on_delete=models.PROTECT)
    student =  models.ForeignKey('student.Student', on_delete=models.PROTECT)
    activeSub = models.ForeignKey('student.PurchasedSubscription', on_delete=models.PROTECT, related_name='activeSub')
    slot = models.ForeignKey('core.TimeSlot',on_delete = models.PROTECT, related_name='timeslot',blank=True,null=True)
    date = models.DateField()
    offtime = models.DurationField(default=datetime.timedelta(hours=0))

    def __str__(self):
        return str(self.student) + str(self.date)

payment_mode_choices = (
    ('Cash', 'Cash'),
    ('Paytm', 'Paytm'),
    ('UPI', 'UPI'),
)
class PurchasedSubscription(models.Model):
    student = models.ForeignKey('student.Student', on_delete=models.PROTECT)

    from_date = models.DateField()
    days = models.PositiveSmallIntegerField()
    shift_timings = models.PositiveSmallIntegerField()

    timeslots = models.ManyToManyField('core.TimeSlot')

    locker = models.ForeignKey('library.LibraryLocker', on_delete=models.PROTECT,null=True,blank=True)
    shift_fees = models.PositiveSmallIntegerField()
    locker_charges = models.PositiveSmallIntegerField()
    total_amount = models.FloatField()

    # subscription = models.ForeignKey('library.LibrarySubscription', on_delete=models.PROTECT)
    date = models.DateField(auto_now_add=True)
    active = models.BooleanField(default=True)
    comment = models.TextField(blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)

    totalOffTime = models.DurationField(default=datetime.timedelta(hours=0))
    totalRollBack = models.DurationField(default=datetime.timedelta(hours=0))
    hoursUtilized = models.DurationField(default=datetime.timedelta(hours=0))
    hoursRemain = models.DurationField(default=datetime.timedelta(hours=0))

    usage50=models.BooleanField(default=False)
    usage85=models.BooleanField(default=False)
    class Meta:
        permissions = (
            ('can_manage_defaulters', 'Can Manage Student Defaulters'),
        )
    
    def __str__(self):
        return str(self.student)+str(self.date)

class StudentPayment(models.Model):
    title = models.CharField(max_length=200,default='')
    purchased_subscription = models.ForeignKey('student.PurchasedSubscription', on_delete=models.PROTECT,blank=True,null=True)
    amount_paid = models.PositiveSmallIntegerField()
    date = models.DateField(auto_now_add=True)
    invoice=models.ImageField(blank=True,null=True)
    payment_mode = models.CharField(max_length=16, choices=payment_mode_choices)

# class StudentAbsent(models.Model):

#     student = models.ForeignKey('student.Student', on_delete=models.PROTECT)
#     purchased_subscription = models.ForeignKey('student.PurchasedSubscription', on_delete=models.PROTECT)
#     date=models.DateField()
#     slot = models.ForeignKey('core.TimeSlot',on_delete = models.PROTECT)

#     def __str__(self):
#         return str(self.student)+str(self.date)

class StudentUBFPayment(models.Model):
    title = models.CharField(max_length=200,default='')
    student = models.ForeignKey('Student',on_delete=models.PROTECT)
    libraryBranch = models.ForeignKey('library.LibraryBranch', on_delete=models.PROTECT)
    amount_paid = models.PositiveSmallIntegerField()
    date = models.DateField(auto_now_add=True)
    payment_mode = models.CharField(max_length=20,default="Razor Pay")
    type = models.CharField(max_length=20,default="ubf income")

    def __str__(self):
        return str(self.student.name)+" "+str(self.title)

@receiver(post_save, sender=Student)
def my_callback(sender, instance, created, *args, **kwargs):
    if created:
        user_subscription = ubfmodels.UserSubscriptions.objects.get_or_create(student=instance)
        #instance.referral_code = uuid.uuid4().hex[:7].upper()
        reward = rewardmodels.RewardSystem.objects.create(student=instance)


@receiver(pre_save, sender=PurchasedSubscription)
def Prepare_sub(sender, instance,*args, **kwargs):
    hours = instance.shift_timings * instance.days
    days = hours//24
    hours = hours-24*days
    if instance._state.adding:
        instance.hoursUtilized = datetime.timedelta(0)
        instance.hoursRemain = datetime.timedelta(days=days,hours=hours)
        instance.totalOffTime = datetime.timedelta(0)
        instance.totalRollBack = datetime.timedelta(0)
        instance.due_date = instance.from_date + datetime.timedelta(days= instance.days-1)
    else:
        print(instance.hoursRemain)
        instance.hoursRemain = datetime.timedelta(days=days,hours=hours) - instance.totalOffTime + instance.totalRollBack - instance.hoursUtilized
        print(instance.hoursRemain)
        hours = instance.totalOffTime.seconds //3600 
        dayslost = hours // instance.shift_timings
        #instance.due_date = instance.from_date + datetime.timedelta(days= instance.days-1) - datetime.timedelta(days=dayslost)




