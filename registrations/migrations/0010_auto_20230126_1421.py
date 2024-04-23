# Generated by Django 3.2.16 on 2023-01-26 14:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registrations', '0009_auto_20221205_1034'),
    ]

    operations = [
        migrations.AddField(
            model_name='registration',
            name='audio_video_kept',
            field=models.CharField(choices=[('yes', 'models:choices:yes'), ('no', 'models:choices:no'), ('n_a', 'models:choices:non_applicable')], default='', max_length=10),
        ),
        migrations.AddField(
            model_name='registration',
            name='audio_video_kept_details',
            field=models.CharField(default='', max_length=250),
        ),
        migrations.AddField(
            model_name='registration',
            name='ic_storage_decade',
            field=models.CharField(choices=[('yes', 'models:choices:yes'), ('no', 'models:choices:no')], default='', max_length=10),
        ),
        migrations.AddField(
            model_name='registration',
            name='ic_storage_location',
            field=models.CharField(blank=True, default='', max_length=250),
        ),
        migrations.AddField(
            model_name='registration',
            name='raw_data_decade',
            field=models.CharField(choices=[('yes', 'models:choices:yes'), ('no', 'models:choices:no')], default='', max_length=10),
        ),
        migrations.AddField(
            model_name='registration',
            name='raw_storage_location',
            field=models.CharField(blank=True, default='', max_length=250),
        ),
        migrations.AlterField(
            model_name='registration',
            name='consent_document_storage',
            field=models.CharField(choices=[('yes', 'models:choices:yes'), ('no', 'models:choices:no'), ('n_a', 'models:choices:non_applicable')], default='', max_length=25),
        ),
        migrations.AlterField(
            model_name='registration',
            name='multimedia_storage',
            field=models.CharField(choices=[('yes', 'models:choices:yes'), ('no', 'models:choices:no'), ('n_a', 'models:choices:non_applicable')], default='', max_length=25),
        ),
    ]
