# Generated by Django 2.2 on 2020-10-20 08:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0002_auto_20201019_1106'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='referral_code',
            field=models.CharField(blank=True, max_length=7, null=True),
        ),
    ]
