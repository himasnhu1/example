# Generated by Django 2.2 on 2020-10-17 07:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('student', '0001_initial'),
        ('core', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0011_update_proxy_permissions'),
        ('library', '0002_auto_20201017_1322'),
    ]

    operations = [
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('image', models.ImageField(blank=True, null=True, upload_to='')),
                ('dob', models.DateField()),
                ('mobile', models.CharField(max_length=10)),
                ('alternate_mobile', models.CharField(blank=True, max_length=10, null=True)),
                ('email', models.EmailField(max_length=254)),
                ('address', models.CharField(max_length=128)),
                ('city', models.CharField(max_length=256)),
                ('state', models.CharField(max_length=16)),
                ('pincode', models.CharField(max_length=6)),
                ('location', models.CharField(max_length=256)),
                ('start_shift', models.TimeField()),
                ('end_shift', models.TimeField()),
                ('id_proof', models.ImageField(blank=True, null=True, upload_to='')),
                ('active', models.BooleanField(default=True)),
                ('branches', models.ManyToManyField(to='library.LibraryBranch')),
                ('library', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='library.Library')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='EmployeeFeedback',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('Feedback', 'Feedback'), ('Complaint', 'Complaint')], max_length=8)),
                ('title', models.CharField(max_length=128)),
                ('details', models.TextField()),
                ('date', models.DateField(auto_now_add=True)),
                ('active', models.BooleanField(default=True)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='owner.Employee')),
                ('library_branch', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='library.LibraryBranch')),
            ],
            options={
                'verbose_name_plural': 'Employee Feedbacks/Complaints',
            },
        ),
        migrations.CreateModel(
            name='Enquiry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('email', models.EmailField(max_length=254)),
                ('mobile', models.CharField(max_length=10)),
                ('preferred_joining_date', models.DateField()),
                ('follow_up_date', models.DateField()),
                ('preferred_shift_time', models.CharField(max_length=128)),
                ('comment', models.TextField()),
                ('status', models.CharField(choices=[('Open', 'Open'), ('Registered', 'Registered'), ('Withdrawed', 'Withdrawed')], default='Open', max_length=10)),
                ('date', models.DateField(auto_now_add=True)),
                ('withdraw_reason', models.TextField(blank=True, null=True)),
                ('exam_preparing_for', models.ManyToManyField(to='core.ExamsPreparingFor')),
                ('library_branch', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='library.LibraryBranch')),
            ],
            options={
                'verbose_name_plural': 'Enquiries',
            },
        ),
        migrations.CreateModel(
            name='Expense',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('title', models.CharField(max_length=128)),
                ('amount', models.PositiveSmallIntegerField()),
                ('payment_mode', models.CharField(choices=[('Cash', 'Cash'), ('Paytm', 'Paytm'), ('UPI', 'UPI')], max_length=16)),
                ('invoice', models.FileField(blank=True, null=True, upload_to='')),
                ('note', models.TextField()),
                ('library_branch', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='library.LibraryBranch')),
            ],
            options={
                'verbose_name_plural': 'Expenses',
            },
        ),
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('Feedback', 'Feedback'), ('Complaint', 'Complaint')], max_length=8)),
                ('title', models.CharField(max_length=128)),
                ('details', models.TextField()),
                ('date', models.DateField(auto_now_add=True)),
                ('active', models.BooleanField(default=True)),
                ('library_branch', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='library.LibraryBranch')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='student.Student')),
            ],
            options={
                'verbose_name_plural': 'Feedbacks/Complaints',
            },
        ),
        migrations.CreateModel(
            name='UserLibraryPermissions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('library_branch', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='library.LibraryBranch')),
                ('permissions', models.ManyToManyField(to='auth.Permission')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Owner/Employee Library Permissions',
                'permissions': (('can_add_permissions', 'Can Add Permissions'), ('can_delete_permissions', 'Can Delete Permissions')),
            },
        ),
        migrations.CreateModel(
            name='Owner',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('image', models.ImageField(blank=True, null=True, upload_to='')),
                ('dob', models.DateField()),
                ('mobile', models.CharField(max_length=10)),
                ('alternate_mobile', models.CharField(blank=True, max_length=10, null=True)),
                ('email', models.EmailField(max_length=254)),
                ('address', models.CharField(max_length=128)),
                ('city', models.CharField(max_length=256)),
                ('state', models.CharField(max_length=16)),
                ('pincode', models.CharField(max_length=6)),
                ('location', models.CharField(max_length=256)),
                ('active', models.BooleanField(default=True)),
                ('branches', models.ManyToManyField(to='library.LibraryBranch')),
                ('library', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='library.Library')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'permissions': (('can_add_partner', 'Can Add Partner'),),
            },
        ),
        migrations.CreateModel(
            name='FeedbackFollowUp',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('detail', models.TextField()),
                ('date', models.DateField(auto_now_add=True)),
                ('expense', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='owner.Expense')),
                ('feedback', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='owner.Feedback')),
            ],
        ),
        migrations.CreateModel(
            name='EnquiryFollowUp',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=128, null=True)),
                ('details', models.TextField()),
                ('next_follow_up_date', models.DateField(blank=True, null=True)),
                ('date', models.DateField(auto_now_add=True)),
                ('enquiry', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='owner.Enquiry')),
            ],
            options={
                'verbose_name_plural': 'Follow-Ups',
            },
        ),
        migrations.CreateModel(
            name='EmployeeFeedbackFollowUp',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('detail', models.TextField()),
                ('date', models.DateField(auto_now_add=True)),
                ('expense', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='owner.Expense')),
                ('feedback', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='owner.EmployeeFeedback')),
            ],
        ),
    ]
