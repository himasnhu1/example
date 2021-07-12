# Generated by Django 2.2 on 2020-10-19 05:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        ('student', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentattendance',
            name='present',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='studentattendance',
            name='slot',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.PROTECT, to='core.TimeSlot'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='studentattendance',
            name='in_time',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.DeleteModel(
            name='StudentAbsent',
        ),
    ]