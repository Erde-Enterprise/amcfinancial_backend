from rest_framework import serializers
        
class LoginSerializer(serializers.Serializer):
    email_or_nickname = serializers.CharField()
    password = serializers.CharField()

class AccessSerializer(serializers.Serializer):
    access_token = serializers.CharField()

class RegisterCostumerSerializer(serializers.Serializer):
    access_token = serializers.CharField()
    name = serializers.CharField()
    nickname = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField()
    photo = serializers.FileField()
    type = serializers.IntegerField()
    