# Generated by Django 2.2 on 2020-10-29 14:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0005_studentubfpayment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentubfpayment',
            name='type',
            field=models.CharField(default='ubf income', max_length=20),
        ),
    ]
