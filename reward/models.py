from django.db import models


class RewardSystem(models.Model):
    student = models.ForeignKey('student.Student',on_delete=models.PROTECT)
    points = models.PositiveIntegerField(default=0)
    claims = models.PositiveIntegerField(default=0)
    totalReferral = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = 'Reward System'
    
    def __str__(self):
        return self.student.name

class RewardCode(models.Model):

    code = models.CharField(max_length=10)
    student = models.ForeignKey('student.Student',on_delete=models.PROTECT)
    max_discount = models.PositiveIntegerField()
    claimed = models.BooleanField(default=False)
    