# Generated by Django 3.2.16 on 2022-12-05 10:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registrations', '0008_rename_type_involved_group_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='InformationKind',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(default='', max_length=200)),
            ],
        ),
        migrations.AddField(
            model_name='registration',
            name='research_goal',
            field=models.TextField(default='', max_length=500),
        ),
    ]