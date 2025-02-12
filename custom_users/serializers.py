from .models import CustomUser, OTP,UserType
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
import random
from django.db import transaction
from app.models import Organizations
class RegisterUserSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email', 'password', 'org','name']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        try:
            with transaction.atomic():
                user = self._create_user(validated_data)
                otp = self._create_and_save_otp(user)
                return user, otp
        except Exception as e:
            raise serializers.ValidationError({"detail": str(e)})

    def _create_user(self, validated_data):
        org = validated_data.pop('org')  # Extract 'org' from validated_data
        return CustomUser.objects.create_user(org=org, **validated_data)

    def _create_and_save_otp(self, user):
        otp = self.generate_otp()
        otp_instance = OTP(user=user)
        otp_instance.set_otp(str(otp))
        otp_instance.save()
        return otp

    @staticmethod
    def generate_otp():
        return random.randint(1000, 9999)
    

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organizations
        fields = ['id', 'name']  # Adjust fields as per your `Organizations` model


class UserTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserType
        fields = ['id', 'name']  # Adjust fields as per your `UserType` model

class CustomUserSerializer(serializers.ModelSerializer):
    org_details = OrganizationSerializer(source='org', read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'id',
            'uuid',
            'email',
            'user_type',
            'is_verified',
            'is_active',
            'is_staff',
            'is_hospital_admin',
            'org',
            'org_details',
        ]
        read_only_fields = ['uuid', 'is_verified', 'is_active', 'is_staff', 'is_hospital_admin']
