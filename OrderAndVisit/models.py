# coding=utf-8

from django.db import models

# Create your models here.
class Hospital(models.Model):
    name = models.CharField(max_length = 20)
    address =  models.CharField(max_length = 100)
    img = models.ImageField(u'图片',upload_to='static/img/hosinfo/')#存储为一个链接
    introduction = models.TextField(null = True)
    phonenum = models.CharField(max_length = 20)

    def __str__(self):
        return self.name

class User(models.Model):
    userName = models.CharField(max_length = 20)
    password = models.CharField(max_length = 100)
    name = models.CharField(max_length = 20)
    sex = models.CharField(max_length = 4)
    birthday = models.CharField(max_length = 20)
    idCard = models.CharField(max_length = 18)
    telephone = models.CharField(max_length = 11)
    creditLevel = models.IntegerField(default = 5)

    def __str__(self):
        return self.userName

class Department(models.Model):
    hospitalId = models.ForeignKey(Hospital)
    name = models.CharField(max_length = 20)
    classinfo = models.CharField(max_length = 20)#科室大类
    introduction = models.TextField(null = True)

    def __str__(self):
        return self.name

class Doctor(models.Model):
    departmentId = models.ForeignKey(Department)
    name = models.CharField(max_length = 10)
    sex = models.CharField(max_length=5)
    title = models.CharField(max_length = 20)
    introduction = models.TextField(null = True)
    address = models.CharField(max_length = 100)
    fee = models.FloatField()#医生的挂号费

    def __str__(self):
        return self.name

class Admin(models.Model):
    userName = models.CharField(max_length = 20)
    userPassword = models.CharField(max_length = 20)

    def __str__(self):
        return self.userName

class VisitMessage(models.Model):
    doctorId = models.ForeignKey(Doctor)
    visitDate = models.CharField(max_length=20)
    visitTime = models.CharField(max_length = 16)#早上/中午/晚上
    maxNumber = models.IntegerField(default = 0)
    restNumber = models.IntegerField(default = 0)#剩余可预约人数

    def __str__(self):
        return self.doctorId.name

class OrderMessage(models.Model):
    userId = models.ForeignKey(User)
    visitId = models.ForeignKey(VisitMessage)
    orderTime = models.DateTimeField(auto_now_add=True)
    isPayed = models.BooleanField(default = False)
    isCanceled = models.BooleanField(default = False)

    def __str__(self):
        return self.userId.name  # + self.visitId + self.orderTime

class RegisterMessage(models.Model):
    orderId = models.ForeignKey(OrderMessage)
    visitId = models.ForeignKey(VisitMessage)
    orderNum = models.IntegerField()

    def __str__(self):
        return self.orderNum

class OrderCancelMessage(models.Model):
    orderId = models.ForeignKey(OrderMessage)
    cancelTime = models.DateTimeField()

class PayMessage(models.Model):
    orderId = models.ForeignKey(OrderMessage)
    value = models.IntegerField()
    type = models.CharField(max_length = 10)
    status = models.CharField(max_length = 20)