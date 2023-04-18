# Generated by Django 3.2.16 on 2023-04-18 15:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registrations', '0020_auto_20230417_1456'),
    ]

    operations = [
        migrations.AlterField(
            model_name='faq',
            name='answer',
            field=models.TextField(blank=True, default='', max_length=5000),
        ),
        migrations.AlterField(
            model_name='faq',
            name='answer_en',
            field=models.TextField(blank=True, default='', max_length=5000, null=True),
        ),
        migrations.AlterField(
            model_name='faq',
            name='answer_nl',
            field=models.TextField(blank=True, default='', max_length=5000, null=True),
        ),
    ]
