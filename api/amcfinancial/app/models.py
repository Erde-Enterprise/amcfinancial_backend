
from django.db import models

class User_Root(models.Model):
    id = models.AutoField(primary_key=True)
    email_Root = models.EmailField(max_length=255)
    password = models.CharField(max_length=255)

class Customer(models.Model):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(max_length=255)
    password = models.CharField(max_length=255)
    type = models.IntegerField()
    root_Id = models.ForeignKey(User_Root, on_delete=models.CASCADE)

class Medical_Clinic(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    color = models.CharField(max_length=255)

class Invoice(models.Model):
    id = models.AutoField(primary_key=True)
    invoice_number = models.CharField(max_length=255)
    description = models.TextField()
    amount = models.IntegerField()
    title = models.CharField(max_length=255)
    issue_date = models.DateField()
    due_date = models.DateField()
    attachment = models.BinaryField(null=True, blank=True)
    reminder = models.IntegerField()
    status = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    clinic_Id = models.ForeignKey(Medical_Clinic, on_delete=models.CASCADE)
    user_Id = models.ForeignKey(Customer, on_delete=models.CASCADE)

class Access_History(models.Model):
    id = models.AutoField(primary_key=True)
    user_Id = models.ForeignKey(User_Root, on_delete=models.CASCADE)
    login_date = models.DateTimeField()
    location = models.CharField(max_length=255)
