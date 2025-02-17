from rest_framework import serializers
from .models import Hostel
from rest_framework import serializers
from .models import Hostel

class HostelSerializer(serializers.ModelSerializer):
    incharge_name = serializers.CharField(source='incharge.name', read_only=True)  # Fetch incharge name

    class Meta:
        model = Hostel
        fields = '__all__'  # Ensuring all fields are included, including `incharge_name`
