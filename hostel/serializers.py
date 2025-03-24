from rest_framework import serializers
from .models import Hostel
from rest_framework import serializers
from .models import Hostel

class HostelSerializer(serializers.ModelSerializer):
    incharge_name = serializers.CharField(source='incharge.name', read_only=True)
    wardens_names = serializers.SerializerMethodField()

    class Meta:
        model = Hostel
        fields = '__all__'
        extra_kwargs = {
            'capacity': {'required': False},  # 👈 This makes it optional for update
        }

    def get_wardens_names(self, obj):
        return [warden.name for warden in obj.wardens.all()]

