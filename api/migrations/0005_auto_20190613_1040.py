# Generated by Django 2.2.1 on 2019-06-13 15:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_auto_20190613_1039'),
    ]

    operations = [
        migrations.AddField(
            model_name='activties',
            name='modver_datetime',
            field=models.CharField(blank=True, default='9999-12-31 00:00:00', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='activtiesdetail',
            name='modver_datetime',
            field=models.CharField(blank=True, default='9999-12-31 00:00:00', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='companyactivties',
            name='modver_datetime',
            field=models.CharField(blank=True, default='9999-12-31 00:00:00', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='companyactivtiesdetail',
            name='modver_datetime',
            field=models.CharField(blank=True, default='9999-12-31 00:00:00', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='companyimages',
            name='modver_datetime',
            field=models.CharField(blank=True, default='9999-12-31 00:00:00', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='companyprofile',
            name='modver_datetime',
            field=models.CharField(blank=True, default='9999-12-31 00:00:00', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='customerimages',
            name='modver_datetime',
            field=models.CharField(blank=True, default='9999-12-31 00:00:00', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='legelentity',
            name='modver_datetime',
            field=models.CharField(blank=True, default='9999-12-31 00:00:00', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='modver_datetime',
            field=models.CharField(blank=True, default='9999-12-31 00:00:00', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='userpic',
            name='modver_datetime',
            field=models.CharField(blank=True, default='9999-12-31 00:00:00', max_length=100, null=True),
        ),
    ]