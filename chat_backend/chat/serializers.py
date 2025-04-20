from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import ChatUser, Message
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatUser
        fields = ['username', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)
    
class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    class Meta:
        model = ChatUser
        fields = ['email', 'password'] 

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatUser
        fields = '__all__' 


class createUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatUser
        fields = ['id','username', 'email', 'password','is_admin','date_joined']
        read_only_fields = ['id','date_joined']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        is_admin = validated_data.pop('is_admin', False)
        user = ChatUser(**validated_data)
        user.set_password(password)
        user.is_admin = is_admin
        user.save()
        return user

class MessageSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    class Meta:
        model = Message
        fields = ['id', 'text', 'created_at', 'role']

    def get_role(self, obj):
        if obj.sender is None:
            return "AI"  # hoặc "system" tùy bạn đặt
        elif obj.sender.is_admin:
            return "admin"
        else:
            return "user"
        

   