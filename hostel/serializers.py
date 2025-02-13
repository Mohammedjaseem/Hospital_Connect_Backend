from rest_framework import serializers
from .models import Hostel

class HostelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hostel
        fields = '__all__' 