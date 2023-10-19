
from django.db import models

class User_Root(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    nickname = models.CharField(max_length=255, unique=True)
    email_Root = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    photo = models.BinaryField(null=True, blank=True)
class Customer(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    nickname = models.CharField(max_length=255, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    photo = models.BinaryField(null=True, blank=True)
    type = models.IntegerField()
    root = models.ForeignKey(User_Root, on_delete=models.SET_NULL, null=True)

class Medical_Clinic(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    color = models.CharField(max_length=255)

class Invoice(models.Model):
    id = models.AutoField(primary_key=True)
    invoice_number = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True)
    amount = models.IntegerField()
    title = models.CharField(max_length=255)
    issue_date = models.DateField()
    due_date = models.DateField()
    attachment = models.BinaryField(null=True, blank=True)
    reminder = models.IntegerField()
    status = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    clinic = models.ForeignKey(Medical_Clinic, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    root = models.ForeignKey(User_Root, on_delete=models.SET_NULL, null=True)

class Access_History(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User_Root, on_delete=models.SET_NULL, null=True)
    login_date = models.DateTimeField()
    location = models.CharField(max_length=255)
