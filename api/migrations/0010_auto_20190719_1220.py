# Generated by Django 2.2.1 on 2019-07-19 17:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_auto_20190719_0419'),
    ]

    operations = [
        migrations.AddField(
            model_name='companyprofile',
            name='activity_status',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='activity_status',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]