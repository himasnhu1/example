from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

class Article(models.Model):
    title = models.CharField(max_length = 512)
    image = models.ImageField()
    date = models.DateField()
    content = models.TextField()

    class Meta:
        verbose_name_plural = 'Articles'
class Category(models.Model):
    name = models.CharField(max_length = 64)

    class Meta:
        verbose_name_plural = 'Categories'

class SubCategory(models.Model):
    category = models.ForeignKey('ubfcore.Category', on_delete=models.PROTECT)
    name = models.CharField(max_length = 64)

    class Meta:
        verbose_name_plural = 'Sub-Categories'

class PDF(models.Model):
    sub_category = models.ForeignKey('ubfcore.SubCategory', on_delete=models.PROTECT)
    name = models.CharField(max_length=256)
    file = models.FileField()
    price = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name_plural = 'PDFs'

class MCQ(models.Model):
    sub_category = models.ForeignKey('ubfcore.SubCategory', on_delete=models.PROTECT)
    name = models.CharField(max_length=256)
    file = models.FileField()
    image = models.ImageField()
    preview_file = models.FileField()
    description = models.TextField(blank=True, null=True)
    price = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name_plural = 'MCQs'

class Summary(models.Model):
    sub_category = models.ForeignKey('ubfcore.SubCategory', on_delete=models.PROTECT)
    name = models.CharField(max_length=256)
    description = models.TextField()
    file = models.FileField()
    image = models.ImageField()
    preview_file = models.FileField()
    price = models.PositiveSmallIntegerField(default=0)
    mcq = models.ManyToManyField('ubfcore.MCQ', null=True)

    class Meta:
        verbose_name_plural = 'Summaries'

class Session(models.Model):
    image = models.ImageField()
    name = models.CharField(max_length = 128)
    date = models.DateField()
    demo = models.FileField(blank=True, null=True)
    video = models.FileField(blank = True, null = True)
    youtube_link = models.CharField(max_length = 512, blank = True, null = True)
    price = models.PositiveSmallIntegerField()

    class Meta:
        verbose_name_plural = 'Sessions'

class UserSubscriptions(models.Model):
    student = models.OneToOneField('student.Student', on_delete=models.PROTECT)
    pdfs = models.ManyToManyField('ubfcore.PDF', blank=True)
    mcqs = models.ManyToManyField('ubfcore.MCQ', blank=True)
    summaries = models.ManyToManyField('ubfcore.Summary', blank=True)
    sessions = models.ManyToManyField('ubfcore.Session', blank=True)
    tests = models.ManyToManyField('ubfquiz.Quiz', blank=True)
    class Meta:
        verbose_name_plural = 'Student Subscriptions'

class GeneralNotification(models.Model):

    title =models.CharField(max_length=250)
    description = models.TextField()
    link = models.URLField(default='',blank=True)
    rollOut = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    


    class Meta:
        verbose_name_plural = 'General Notification'
    
    def __str__(self):
        return self.title

# class PromoCode(models.Model):

#     code = models.CharField(max_length = 6)
#     percent = models.PositiveSmallIntegerField()
#     description = models.TextField(blank=True)
#     timestamp = models.DateTimeField(auto_now_add= True)
#     active = models.BooleanField(default=False)

#     class Meta:
#         verbose_name_plural = 'Promo Codes'

# class UserCode(models.Model):

#     user = models.ForeignKey('core.User', on_delete=models.PROTECT)
#     code = models.ForeignKey('core.PromoCode',on_delete=models.PROTECT)
#     timestamp = models.DateTimeField(auto_now_add= True)

#     class Meta:
#         verbose_name_plural = 'Promocodes Used (User)'

# @receiver(post_save, sender=)
# def my_callback(sender, instance, *args, **kwargs):
#     user_subscription = UserSubscriptions.objects.get_or_create(user=instance)

# @receiver(pre_save, sender = PersonalNotification)
# def my_call(sender,instance,*args,**kwargs):

#     instance.message = str(instance.quiz.name)+" has been purchased. Your quiz is scheduled on :"



