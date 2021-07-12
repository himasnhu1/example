from django.db import models
from django.db.models.signals import pre_save,post_save

# Create your models here.
class Library(models.Model):
    name = models.CharField(max_length=128)

    date = models.DateField(auto_now_add=True)
    active = models.BooleanField(default=False)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name_plural = 'Libraries'
        permissions = (
            ('can_view_qr_code', 'Can View QR Code'),
        )

    def branches(self):
        branches = LibraryBranch.objects.filter(library = self)
        return branches

months_choices = (
    (1, 'January'),
    (2, 'February'),
    (3, 'March'),
    (4, 'April'),
    (5, 'May'),
    (6, 'June'),
    (7, 'July'),
    (8, 'August'),
    (9, 'September'),
    (10, 'October'),
    (11, 'November'),
    (12, 'December'),
)
class LibraryBranch(models.Model):
    library = models.ForeignKey('library.Library', on_delete=models.PROTECT)
    name = models.CharField(max_length=128)
    logo = models.ImageField(blank=True, null=True)

    seat_capacity = models.PositiveSmallIntegerField()
    no_of_booking_per_slot = models.PositiveSmallIntegerField()
    no_of_lockers = models.PositiveSmallIntegerField()

    opening_days = models.ManyToManyField('core.OpeningDays',blank=True,null=True)
    opening_time = models.TimeField(blank=True,null=True)
    closing_time = models.TimeField(blank=True,null=True)

    night_shift_from = models.TimeField(blank=True,null=True)
    night_shift_to = models.TimeField(blank=True,null=True)

    description = models.TextField(blank=True,null=True)

    beginning_of_summer_season = models.PositiveSmallIntegerField(choices=months_choices,blank=True,null=True)
    beginning_of_winter_season = models.PositiveSmallIntegerField(choices=months_choices,blank=True,null=True)

    address = models.TextField(blank=True,null=True)
    city = models.CharField(max_length=256,blank=True,null=True)
    state = models.CharField(max_length=16,blank=True,null=True)
    pincode = models.CharField(max_length=6,blank=True,null=True)
    location = models.CharField(max_length=256,blank=True,null=True)

    admission_fees = models.PositiveSmallIntegerField(blank=True,null=True)
    locker_fees = models.PositiveSmallIntegerField(blank=True,null=True)
    gst = models.FloatField(blank=True,null=True)
    ammenities = models.ManyToManyField('core.Ammenity',blank=True,null=True)

    image1 = models.ImageField(blank=True,null=True)
    image2 = models.ImageField(blank=True,null=True)
    image3 = models.ImageField(blank=True,null=True)
    image4 = models.ImageField(blank=True,null=True)
    image5 = models.ImageField(blank=True,null=True)
    image6 = models.ImageField(blank=True,null=True)
    image7 = models.ImageField(blank=True,null=True)
    image8 = models.ImageField(blank=True,null=True)
    image9 = models.ImageField(blank=True,null=True)
    image10 = models.ImageField(blank=True,null=True)

    date = models.DateField(auto_now_add=True)
    active = models.BooleanField(default=False)

    activeSub = models.BooleanField(default=True)

    report = models.FileField(null=True,blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Library Branches'


class LibraryLocker(models.Model):
    library_branch = models.ForeignKey('library.LibraryBranch', on_delete=models.PROTECT)
    locker_number = models.CharField(max_length=64)
    assigned_student = models.ForeignKey('student.Student', on_delete=models.PROTECT, null=True, blank=True)
    date = models.DateField(auto_now_add=True)
    active = models.BooleanField(default=False)

    def __str__(self):
        return str(self.library_branch) + '-' + str(self.id)

class LibrarySubscription(models.Model):
    library_branch = models.ForeignKey('library.LibraryBranch', on_delete=models.PROTECT)
    no_of_hours = models.PositiveSmallIntegerField()
    summer_base_charges = models.PositiveSmallIntegerField()
    winter_base_charges = models.PositiveSmallIntegerField()
    date = models.DateField(auto_now_add=True)
    nightShift = models.BooleanField(default=False)
    active = models.BooleanField(default=False)

    def __str__(self):
        return str(self.library_branch) + ': ' + str(self.no_of_hours)+ ': ' + str(self.no_of_hours)

    class Meta:
        verbose_name_plural = 'Subscriptions'

class Holidays(models.Model):
    library_branch = models.ForeignKey('library.LibraryBranch', on_delete=models.PROTECT)
    title = models.CharField(max_length=256)
    details = models.TextField()
    start = models.DateField()
    end = models.DateField()
    date = models.DateField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = 'Holidays'


class LibraryOffer(models.Model):
    library = models.ForeignKey('library.LibraryBranch', on_delete=models.PROTECT)
    start = models.DateTimeField()
    end = models.DateTimeField()
    title = models.CharField(max_length=256)
    description = models.TextField()
    tnc = models.TextField()
    date = models.DateField(auto_now_add=True)
    active = models.BooleanField(default=False)
    file = models.FileField()

    def __str__(self):
        return str(self.title)

class AttendanceQrCode(models.Model):

    branch = models.ForeignKey('library.LibraryBranch', on_delete=models.PROTECT)
    qrcode = models.CharField(max_length=32)
    active = models.BooleanField(default=False)
    date = models.DateField(auto_now_add=True)
    class Meta:
        verbose_name_plural = 'Attendance Qr Code'

    def __str__(self):
        return str(self.branch) + self.qrcode

# @receiver(post_save, sender=LibraryBranch)
# def building_lockers(sender, instance,created,*args, **kwargs):
#     # if instance._state.adding:
#     if created :
#         for i in range(1,instance.no_of_lockers+1):
#             locker = LibraryLocker.create(library_branch=instance,locker = 'Locker '+str(i),active=True)
