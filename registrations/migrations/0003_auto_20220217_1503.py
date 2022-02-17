# Generated by Django 3.2.11 on 2022-02-17 15:03

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('registrations', '0002_auto_20220215_1127'),
    ]

    operations = [
        migrations.AddField(
            model_name='registration',
            name='faculty',
            field=models.CharField(blank=True, default=None, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='registration',
            name='applicants',
            field=models.ManyToManyField(blank=True, related_name='applicant_for', to=settings.AUTH_USER_MODEL),
        ),
    ]
