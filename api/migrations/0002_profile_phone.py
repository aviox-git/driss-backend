# Generated by Django 2.2.1 on 2019-06-13 14:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='phone',
            field=models.BigIntegerField(null=True, verbose_name='Phone Number'),
        ),
    ]
