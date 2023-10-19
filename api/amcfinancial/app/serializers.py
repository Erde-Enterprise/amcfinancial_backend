from rest_framework import serializers
from .models import Customer
from .models import User_Root

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'

class UserRootSerializer(serializers.ModelSerializer):
    class Meta:
        model = User_Root
        fields = '__all__'
        
class LoginSerializer(serializers.Serializer):
    email_or_nickname = serializers.CharField()
    password = serializers.CharField()

class AccessSerializer(serializers.Serializer):
    access_token = serializers.CharField()