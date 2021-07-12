from django.db import models
from django.contrib.auth.models import AbstractUser
#from fcm_django.models import AbstractDevice
from fcm.models import AbstractDevice
import datetime
from django.db.models.signals import pre_save,post_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template import Context
from django.template.loader import render_to_string
from django.utils.html import strip_tags

user_type = (
    ('Student', 'Student'),
    ('Owner', 'Owner'),
    ('Employee','Employee')
)

class User(AbstractUser):
    is_admin = models.BooleanField(default=False)
    is_owner = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)
    is_employee = models.BooleanField(default=False)
    notification_token = models.CharField(max_length=64, blank=True, null=True)
    passwordchanged = models.BooleanField(default=False)

class MyDevice(AbstractDevice):
    user = models.ForeignKey(User,on_delete=models.PROTECT)


class HigherEducation(models.Model):
    title = models.CharField(max_length=128)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = 'Higher Education'

class ExamsPreparingFor(models.Model):
    title = models.CharField(max_length=128)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = 'Exams Preparing For'

class OpeningDays(models.Model):
    day = models.CharField(max_length=16)

    def __str__(self):
        return self.day

    class Meta:
        verbose_name_plural = 'Opening Days'

class TimeSlot(models.Model):
    # library_branch = models.ForeignKey('core.LibraryBranch', on_delete=models.PROTECT)
    start = models.TimeField()
    end = models.TimeField()
    active = models.BooleanField(default=True)
    # slots = models.PositiveSmallIntegerField()
    # remaining_slots = models.PositiveSmallIntegerField()

    def __str__(self):
        return str(self.start) + '-' + str(self.end)

class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=40)
    days = models.PositiveSmallIntegerField()
    branches_allowed = models.PositiveSmallIntegerField()
    date = models.DateField(auto_now_add=True)

class SubscriptionPayment(models.Model):
    subscription_plan = models.ForeignKey('core.SubscriptionPlan', on_delete=models.PROTECT)
    payment_mode = models.CharField(max_length=16)

    date = models.DateField(auto_now_add=True)


class Feedback(models.Model):
    user = models.ForeignKey('core.User', on_delete=models.PROTECT)
    feedback = models.TextField()
    date = models.DateField(auto_now_add=True)

class Incident(models.Model):
    user = models.ForeignKey('core.User', on_delete=models.PROTECT)
    title = models.CharField(max_length=256)
    details = models.TextField()
    image = models.ImageField()
    date = models.DateField(auto_now_add=True)
    ticket = models.CharField(max_length=126)
    active = models.BooleanField(default=True)
    inactive = models.BooleanField(default=False)

    def __str__(self):
        return self.ticket
class FAQ(models.Model):

    user_type = models.CharField(max_length=16,choices=user_type)
    question = models.CharField(max_length=256)
    answer = models.TextField()
    date = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Frequently Asked Questions'

class Notification(models.Model):
    user = models.ForeignKey('core.User', on_delete=models.PROTECT)
    subject = models.CharField(max_length=128)
    message = models.TextField()
    date = models.DateField(auto_now_add=True)

# Current Affair Models
class CurrentAffairCategory(models.Model):
    title = models.CharField(max_length=128)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Current Affair Categories'

    def __str__(self):
        return str(self.title)

class CurrentAffair(models.Model):
    category = models.ForeignKey('core.CurrentAffairCategory', on_delete=models.PROTECT)
    title = models.CharField(max_length=512)
    posted_by = models.CharField(max_length=128)
    description = models.TextField()

    def __str__(self):
        return str(self.title)

class CurrentAffairImage(models.Model):
    current_affair = models.ForeignKey('core.CurrentAffair', on_delete=models.PROTECT)
    image = models.ImageField()

class Ammenity(models.Model):
    name = models.CharField(max_length=128)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name_plural = 'Ammenities'

class Notifications(models.Model):

    student = models.ForeignKey('student.Student',on_delete=models.PROTECT)
    title = models.CharField(max_length=150)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    notifType = models.CharField(max_length=50)

    def __str__(self):
        return str(self.student.name)+str(self.title)
    
    class Meta:
        verbose_name_plural = 'Student Notifications'

@receiver(pre_save, sender=Incident)
def mailing(sender, instance,*args, **kwargs):
    if instance._state.adding:
        pass
    else:
        if instance.active==False:
            instance.inactive=True
            html_content = render_to_string('core/incident-complete.html',{"ticket":instance.ticket})
            text_content = strip_tags(html_content)
            email = EmailMultiAlternatives('Incident Completed '+str(instance.ticket), text_content,'testingserver.12307@gmail.com',[instance.user.email,"yashch1998@gmail.com",])
            email.attach_alternative(html_content, "text/html")

            email.send()







