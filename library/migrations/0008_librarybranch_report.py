# Generated by Django 2.2 on 2020-11-11 19:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0007_librarybranch_activesub'),
    ]

    operations = [
        migrations.AddField(
            model_name='librarybranch',
            name='report',
            field=models.FileField(blank=True, null=True, upload_to=''),
        ),
    ]