# Generated by Django 2.2 on 2020-10-17 07:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AttendanceQrCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('qrcode', models.CharField(max_length=32)),
                ('active', models.BooleanField(default=False)),
                ('date', models.DateField(auto_now_add=True)),
            ],
            options={
                'verbose_name_plural': 'Attendance Qr Code',
            },
        ),
        migrations.CreateModel(
            name='Holidays',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=256)),
                ('details', models.TextField()),
                ('start', models.DateField()),
                ('end', models.DateField()),
                ('date', models.DateField(auto_now_add=True)),
                ('active', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name_plural': 'Holidays',
            },
        ),
        migrations.CreateModel(
            name='Library',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('date', models.DateField(auto_now_add=True)),
                ('active', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name_plural': 'Libraries',
                'permissions': (('can_view_qr_code', 'Can View QR Code'),),
            },
        ),
        migrations.CreateModel(
            name='LibraryBranch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('logo', models.ImageField(blank=True, null=True, upload_to='')),
                ('seat_capacity', models.PositiveSmallIntegerField()),
                ('no_of_booking_per_slot', models.PositiveSmallIntegerField()),
                ('no_of_lockers', models.PositiveSmallIntegerField()),
                ('opening_time', models.TimeField()),
                ('closing_time', models.TimeField()),
                ('night_shift_from', models.TimeField()),
                ('night_shift_to', models.TimeField()),
                ('description', models.TextField()),
                ('beginning_of_summer_season', models.PositiveSmallIntegerField(choices=[(1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'), (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'), (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')])),
                ('beginning_of_winter_season', models.PositiveSmallIntegerField(choices=[(1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'), (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'), (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')])),
                ('address', models.TextField()),
                ('city', models.CharField(blank=True, max_length=256, null=True)),
                ('state', models.CharField(blank=True, max_length=16, null=True)),
                ('pincode', models.CharField(blank=True, max_length=6, null=True)),
                ('location', models.CharField(blank=True, max_length=256, null=True)),
                ('admission_fees', models.PositiveSmallIntegerField()),
                ('locker_fees', models.PositiveSmallIntegerField()),
                ('gst', models.FloatField()),
                ('date', models.DateField(auto_now_add=True)),
                ('active', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name_plural': 'Library Branches',
            },
        ),
        migrations.CreateModel(
            name='LibraryLocker',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('locker_number', models.CharField(max_length=64)),
                ('date', models.DateField(auto_now_add=True)),
                ('active', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='LibrarySubscription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('no_of_hours', models.PositiveSmallIntegerField()),
                ('summer_base_charges', models.PositiveSmallIntegerField()),
                ('winter_base_charges', models.PositiveSmallIntegerField()),
                ('date', models.DateField(auto_now_add=True)),
                ('active', models.BooleanField(default=False)),
                ('library_branch', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='library.LibraryBranch')),
            ],
            options={
                'verbose_name_plural': 'Subscriptions',
            },
        ),
        migrations.CreateModel(
            name='LibraryOffer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start', models.DateTimeField()),
                ('end', models.DateTimeField()),
                ('title', models.CharField(max_length=256)),
                ('description', models.TextField()),
                ('coupon_code', models.CharField(blank=True, max_length=126, null=True)),
                ('website', models.CharField(blank=True, max_length=126, null=True)),
                ('tnc', models.TextField()),
                ('date', models.DateField(auto_now_add=True)),
                ('active', models.BooleanField(default=False)),
                ('file', models.FileField(upload_to='')),
                ('library', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='library.LibraryBranch')),
            ],
        ),
    ]