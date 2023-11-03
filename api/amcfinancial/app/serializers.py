from rest_framework import serializers
from .models import Invoice, Medical_Clinic
        
class LoginSerializer(serializers.Serializer):
    email_or_nickname = serializers.CharField()
    password = serializers.CharField()

class RegisterCostumerSerializer(serializers.Serializer):
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
    status = serializers.CharField()
    type = serializers.CharField()
    name_clinic = serializers.CharField()

class MedicalClinicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medical_Clinic
        fields = ('name','color')
class ListInvoicesSerializer(serializers.ModelSerializer):
    clinic = MedicalClinicSerializer()
    class Meta:
        model = Invoice
        exclude =('id','attachment','user')


