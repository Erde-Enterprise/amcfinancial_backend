from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Invoice, Medical_Clinic, Customer, User_Root
        
# Requests
class LoginSerializer(serializers.Serializer):
    email_or_nickname = serializers.CharField()
    password = serializers.CharField()

class RegisterCustomerSerializer(serializers.Serializer):
    name = serializers.CharField()
    nickname = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField()
    photo = serializers.ImageField(required=False)
    type = serializers.IntegerField() 

class RegisterClinicSerializer(serializers.Serializer):
    name = serializers.CharField()
    color = serializers.CharField()

class RegisterInvoiceSerializer(serializers.Serializer):
    invoice_number = serializers.CharField()
    description = serializers.CharField(required=False)
    amount = serializers.IntegerField()
    title = serializers.CharField()
    issue_date = serializers.DateField()
    due_date = serializers.DateField()
    attachment = serializers.FileField()
    reminder = serializers.IntegerField(required=False)
    status = serializers.CharField()
    type = serializers.CharField()
    name_clinic = serializers.CharField()
    
class AttachmentSerializer(serializers.Serializer):
    invoice_number = serializers.CharField()

class CustomerSerializer(serializers.Serializer):
    nickname = serializers.CharField()

class InvoiceSerializer(serializers.Serializer):
    invoice_number = serializers.CharField()

class ClinicSerializer(serializers.Serializer):
    name = serializers.CharField()

class UpdateInvoiceSerializer(serializers.Serializer):
    invoice_number_older = serializers.CharField()
    invoice_number = serializers.CharField(required=False)
    description = serializers.CharField(required=False)
    amount = serializers.IntegerField(required=False)
    title = serializers.CharField(required=False)
    issue_date = serializers.DateField(required=False)
    due_date = serializers.DateField(required=False)
    attachment = serializers.FileField(required=False)
    reminder = serializers.IntegerField(required=False)
    status = serializers.CharField(required=False)
    type = serializers.CharField(required=False)
    name_clinic = serializers.CharField(required=False)


# Responses
class MedicalClinicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medical_Clinic
        fields = ('name','color')

class ListInvoicesSerializer(serializers.ModelSerializer):
    clinic = MedicalClinicSerializer()
    class Meta:
        model = Invoice
        exclude =('id','attachment','user')

class ListClinicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medical_Clinic
        fields = ('name','color')

class ListCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ('name','nickname','email','photo','type')

class LoginCustomerResponseSerializer(serializers.ModelSerializer):
    token = serializers.SerializerMethodField()
    class Meta:
        model = Customer
        fields = ('token','name','nickname','email','photo','type')
    
    def get_token(self, obj):
        refresh = RefreshToken.for_user(obj)
        refresh['type'] = obj.type
        return str(refresh)

class LoginUserRootResponseSerializer(serializers.ModelSerializer):
    type = serializers.IntegerField(default=0)
    token = serializers.SerializerMethodField()
    class Meta:
        model = User_Root
        fields = ('token','name','nickname','email_root','photo', 'type')

    def get_token(self, obj):
        refresh = RefreshToken.for_user(obj)
        refresh['type'] = 0
        return str(refresh)