# Generated by Django 2.2.1 on 2019-06-13 15:39

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_auto_20190613_1000'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='activties',
            name='modver_datetime',
        ),
        migrations.RemoveField(
            model_name='activtiesdetail',
            name='modver_datetime',
        ),
        migrations.RemoveField(
            model_name='companyactivties',
            name='modver_datetime',
        ),
        migrations.RemoveField(
            model_name='companyactivtiesdetail',
            name='modver_datetime',
        ),
        migrations.RemoveField(
            model_name='companyimages',
            name='modver_datetime',
        ),
        migrations.RemoveField(
            model_name='companyprofile',
            name='modver_datetime',
        ),
        migrations.RemoveField(
            model_name='customerimages',
            name='modver_datetime',
        ),
        migrations.RemoveField(
            model_name='legelentity',
            name='modver_datetime',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='modver_datetime',
        ),
        migrations.RemoveField(
            model_name='userpic',
            name='modver_datetime',
        ),
        migrations.AlterField(
            model_name='activties',
            name='create_datetime',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True),
        ),
        migrations.AlterField(
            model_name='activtiesdetail',
            name='create_datetime',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True),
        ),
        migrations.AlterField(
            model_name='companyactivties',
            name='create_datetime',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True),
        ),
        migrations.AlterField(
            model_name='companyactivtiesdetail',
            name='create_datetime',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True),
        ),
        migrations.AlterField(
            model_name='companyimages',
            name='create_datetime',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True),
        ),
        migrations.AlterField(
            model_name='companyprofile',
            name='create_datetime',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True),
        ),
        migrations.AlterField(
            model_name='customerimages',
            name='create_datetime',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True),
        ),
        migrations.AlterField(
            model_name='forgotcode',
            name='create_datetime',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True),
        ),
        migrations.AlterField(
            model_name='legelentity',
            name='create_datetime',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='create_datetime',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True),
        ),
        migrations.AlterField(
            model_name='userpic',
            name='create_datetime',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True),
        ),
    ]
