from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import ValidationError

from .models import Invoice, Medical_Clinic, Customer, User_Root
from .provides import get_file_mime_type
        
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
    invoices_number = serializers.ListField(child=serializers.CharField())

class ClinicSerializer(serializers.Serializer):
    name = serializers.CharField()

class UpdateInvoiceSerializer(serializers.Serializer):
    invoice_number = serializers.CharField()
    new_invoice_number = serializers.CharField(required=False)
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

    def update(self, instance, validated_data):
        try:
            if 'attachment' in validated_data:
                attachment_file = validated_data['attachment'].read()
                instance.attachment = attachment_file

            if 'name_clinic' in validated_data:
                name_clinic = validated_data['name_clinic']
                clinic = Medical_Clinic.objects.get(name=name_clinic)
                instance.clinic = clinic
            
            instance.invoice_number = validated_data.get('new_invoice_number', instance.invoice_number)
            instance.description = validated_data.get('description', instance.description)
            instance.amount = validated_data.get('amount', instance.amount)
            instance.title = validated_data.get('title', instance.title)
            instance.issue_date = validated_data.get('issue_date', instance.issue_date)
            instance.due_date = validated_data.get('due_date', instance.due_date)
            instance.reminder = validated_data.get('reminder', instance.reminder)
            instance.status = validated_data.get('status', instance.status)
            instance.type = validated_data.get('type', instance.type)
            instance.save()
            return instance
        except Medical_Clinic.DoesNotExist:
            raise ValidationError('Clinic not found')

class UpdateCustomerSerializer(serializers.Serializer):
    nickname = serializers.CharField()
    new_nickname = serializers.CharField(required=False)
    name = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    password = serializers.CharField(required=False)
    photo = serializers.ImageField(required=False)
    type = serializers.IntegerField(required=False)

    def update(self, instance, validated_data):
        try:
            if 'photo' in validated_data:
                photo = validated_data['photo'].read()
                instance.photo = photo
                
            instance.nickname = validated_data.get('new_nickname', instance.nickname)
            instance.name = validated_data.get('name', instance.name)
            instance.email = validated_data.get('email', instance.email)
            instance.password = validated_data.get('password', instance.password)
            instance.type = validated_data.get('type', instance.type)
            instance.save()
            return instance
        except:
            raise ValidationError('Invalid data')

# Responses
class ListClinicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medical_Clinic
        fields = ('name','color')

class ListInvoicesSerializer(serializers.ModelSerializer):
    clinic = ListClinicSerializer()
    class Meta:
        model = Invoice
        exclude =('id','attachment','user', 'searchable')

class ListCustomerSerializer(serializers.ModelSerializer):
    mime_type = serializers.SerializerMethodField()
    def get_mime_type(self, obj):
        photo = obj.photo
        return get_file_mime_type(photo)
    class Meta:
        model = Customer
        fields = ('name','nickname','email','photo', 'mime_type','type')

class LoginCustomerResponseSerializer(serializers.ModelSerializer):
    token = serializers.SerializerMethodField()
    mime_type = serializers.SerializerMethodField()
    class Meta:
        model = Customer
        fields = ('token','name','nickname','email','photo','mime_type','type')
    
    def get_token(self, obj):
        refresh = RefreshToken.for_user(obj)
        refresh['type'] = obj.type
        return str(refresh)
    
    def get_mime_type(self, obj):
        photo = obj.photo
        return get_file_mime_type(photo)
    
class LoginUserRootResponseSerializer(serializers.ModelSerializer):
    type = serializers.IntegerField(default=0)
    token = serializers.SerializerMethodField()
    mime_type = serializers.SerializerMethodField()
    class Meta:
        model = User_Root
        fields = ('token','name','nickname','email_root','photo','mime_type', 'type')

    def get_token(self, obj):
        refresh = RefreshToken.for_user(obj)
        refresh['type'] = 0
        return str(refresh)
    
    def get_mime_type(self, obj):
        photo = obj.photo
        return get_file_mime_type(photo)