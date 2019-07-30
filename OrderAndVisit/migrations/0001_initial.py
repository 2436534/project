# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Admin',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('userName', models.CharField(max_length=20)),
                ('userPassword', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=20)),
                ('classinfo', models.CharField(max_length=20)),
                ('introduction', models.TextField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Doctor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=10)),
                ('sex', models.CharField(max_length=5)),
                ('title', models.CharField(max_length=20)),
                ('introduction', models.TextField(null=True)),
                ('address', models.CharField(max_length=100)),
                ('fee', models.FloatField()),
                ('departmentId', models.ForeignKey(to='OrderAndVisit.Department')),
            ],
        ),
        migrations.CreateModel(
            name='Hospital',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=20)),
                ('address', models.CharField(max_length=100)),
                ('img', models.CharField(max_length=50)),
                ('introduction', models.TextField(null=True)),
                ('phonenum', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='OrderCancelMessage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('cancelTime', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='OrderMessage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('orderTime', models.DateTimeField(auto_now_add=True)),
                ('isPayed', models.BooleanField(default=False)),
                ('isCanceled', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='PayMessage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('value', models.IntegerField()),
                ('type', models.CharField(max_length=10)),
                ('status', models.CharField(max_length=20)),
                ('orderId', models.ForeignKey(to='OrderAndVisit.OrderMessage')),
            ],
        ),
        migrations.CreateModel(
            name='RegisterMessage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('orderNum', models.IntegerField()),
                ('orderId', models.ForeignKey(to='OrderAndVisit.OrderMessage')),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('userName', models.CharField(max_length=20)),
                ('password', models.CharField(max_length=100)),
                ('name', models.CharField(max_length=20)),
                ('sex', models.CharField(max_length=4)),
                ('birthday', models.CharField(max_length=20)),
                ('idCard', models.CharField(max_length=18)),
                ('telephone', models.CharField(max_length=11)),
                ('creditLevel', models.IntegerField(default=5)),
            ],
        ),
        migrations.CreateModel(
            name='VisitMessage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('visitDate', models.CharField(max_length=20)),
                ('visitTime', models.CharField(max_length=16)),
                ('maxNumber', models.IntegerField(default=0)),
                ('restNumber', models.IntegerField(default=0)),
                ('doctorId', models.ForeignKey(to='OrderAndVisit.Doctor')),
            ],
        ),
        migrations.AddField(
            model_name='registermessage',
            name='visitId',
            field=models.ForeignKey(to='OrderAndVisit.VisitMessage'),
        ),
        migrations.AddField(
            model_name='ordermessage',
            name='userId',
            field=models.ForeignKey(to='OrderAndVisit.User'),
        ),
        migrations.AddField(
            model_name='ordermessage',
            name='visitId',
            field=models.ForeignKey(to='OrderAndVisit.VisitMessage'),
        ),
        migrations.AddField(
            model_name='ordercancelmessage',
            name='orderId',
            field=models.ForeignKey(to='OrderAndVisit.OrderMessage'),
        ),
        migrations.AddField(
            model_name='department',
            name='hospitalId',
            field=models.ForeignKey(to='OrderAndVisit.Hospital'),
        ),
    ]
