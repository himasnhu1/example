from django.db import models

# Create your models here.
class UserCart(models.Model):
    student = models.ForeignKey('student.Student', on_delete=models.PROTECT)
    pdfs = models.ManyToManyField('ubfcore.PDF', blank=True)
    mcqs = models.ManyToManyField('ubfcore.MCQ', blank=True)
    summaries = models.ManyToManyField('ubfcore.Summary', blank=True)
    sessions = models.ManyToManyField('ubfcore.Session', blank=True)
    tests = models.ManyToManyField('ubfquiz.Quiz', blank=True)

    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField(blank=True, null=True)
    ordered = models.BooleanField(default=False)
    order_id = models.CharField(max_length=64,blank=True,null=True)
    payment = models.ForeignKey('ubfcart.Payment', on_delete=models.PROTECT, blank=True, null=True)

    single_product = models.BooleanField(default=False)
    promocode = models.ForeignKey('Promocode',on_delete=models.PROTECT,blank=True, null=True)
    rewardcode = models.ForeignKey('reward.RewardCode',on_delete=models.PROTECT,blank=True, null=True)
    #codetype = models.CharField(max_length=10,null=True,blank=True)
    amount = models.PositiveIntegerField(blank=True,null=True)

    class Meta:
        verbose_name_plural = 'Carts'

class Bookmark(models.Model):
    student = models.ForeignKey('student.Student', on_delete=models.PROTECT)
    pdfs = models.ManyToManyField('ubfcore.PDF', blank=True)
    mcqs = models.ManyToManyField('ubfcore.MCQ', blank=True)
    summaries = models.ManyToManyField('ubfcore.Summary', blank=True)
    sessions = models.ManyToManyField('ubfcore.Session', blank=True)
    tests = models.ManyToManyField('ubfquiz.Quiz', blank=True)
    class Meta:
        verbose_name_plural = 'Bookmarks'

class SaveForLater(models.Model):
    student = models.ForeignKey('student.Student', on_delete=models.PROTECT)
    pdfs = models.ManyToManyField('ubfcore.PDF', blank=True)
    mcqs = models.ManyToManyField('ubfcore.MCQ', blank=True)
    summaries = models.ManyToManyField('ubfcore.Summary', blank=True)
    sessions = models.ManyToManyField('ubfcore.Session', blank=True)
    tests = models.ManyToManyField('ubfquiz.Quiz', blank=True)

    class Meta:
        verbose_name_plural = 'Saved For Later'

class Payment(models.Model):
    amount = models.PositiveIntegerField()
    order_id = models.CharField(max_length=128)
    payment_id = models.CharField(max_length=128)
    date_time = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'Payments'

class Promocode(models.Model):
    code=models.CharField(max_length=7,unique=True)
    title = models.CharField(max_length=100,default="")
    description = models.TextField(default="")
    discountpercent = models.FloatField(null=True,blank=True)
    max_discount = models.PositiveSmallIntegerField(null=True,blank=True)
    active = models.BooleanField(default=True)
    validity = models.DateField(null=True,blank=True)
    createdOn = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'UBF promocodes'