from django.db import models


class Studentpaymentorder(models.Model):

    student = models.ForeignKey('student.Student',on_delete=models.PROTECT)
    amount = models.PositiveSmallIntegerField()
    order_id = models.CharField(max_length=128,blank=True,null=True)
    payment_id = models.CharField(max_length=128,blank=True,null=True)
    date_time = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'Payments'
