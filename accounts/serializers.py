from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['phone_number']


class CustomUserOtpSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['otp_code']
