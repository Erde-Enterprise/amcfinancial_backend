
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class User_Root(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    nickname = models.CharField(max_length=255, unique=True)
    email_root = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    photo = models.BinaryField(null=True, blank=True)
    searchable = models.BooleanField(default=True)
    
class Customer(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    nickname = models.CharField(max_length=255, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    photo = models.BinaryField(null=True, blank=True)
    type = models.IntegerField()
    searchable = models.BooleanField(default=True)
    root = models.ForeignKey(User_Root, on_delete=models.SET_NULL, null=True)

class UserProfile(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True)
    object_id = models.PositiveIntegerField()
    user = GenericForeignKey('content_type', 'object_id')

class Medical_Clinic(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    color = models.CharField(max_length=255)
    searchable = models.BooleanField(default=True)

class Invoice(models.Model):
    id = models.AutoField(primary_key=True)
    invoice_number = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    title = models.CharField(max_length=255)
    issue_date = models.DateField()
    due_date = models.DateField()
    attachment = models.BinaryField(null=True, blank=True)
    reminder = models.IntegerField()
    status = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    searchable = models.BooleanField(default=True)
    clinic = models.ForeignKey(Medical_Clinic, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True)


class Access_History(models.Model):
    id = models.AutoField(primary_key=True)
    login_date = models.DateTimeField()
    location = models.CharField(max_length=255)
    searchable = models.BooleanField(default=True)
    user = models.ForeignKey(User_Root, on_delete=models.SET_NULL, null=True)

