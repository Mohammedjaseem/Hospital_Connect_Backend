from rest_framework import serializers
from .models import Hostel
from rest_framework import serializers
from .models import Hostel

class HostelSerializer(serializers.ModelSerializer):
    incharge_name = serializers.CharField(source='incharge.name', read_only=True)  # Fetch incharge name
    wardens_names = serializers.SerializerMethodField()  # Custom method to fetch wardens' names

    class Meta:
        model = Hostel
        fields = '__all__'  # Ensuring all fields are included, including `incharge_name`
        
    def get_wardens_names(self, obj):
        return [warden.name for warden in obj.wardens.all()]  # Assuming `wardens` is a related name in Hostel model
