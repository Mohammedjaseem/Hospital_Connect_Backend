from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Hostel
from .serializers import HostelSerializer

# ✅ Create Hostel
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_hostel(request):
    serializer = HostelSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ✅ View All Hostels
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_hostels(request):
    hostels = Hostel.objects.all()
    serializer = HostelSerializer(hostels, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

# ✅ View Single Hostel
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_hostel(request, hostel_id):
    try:
        hostel = Hostel.objects.get(id=hostel_id)
    except Hostel.DoesNotExist:
        return Response({"error": "Hostel not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = HostelSerializer(hostel)
    return Response(serializer.data, status=status.HTTP_200_OK)

# ✅ Update Hostel
@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
# @authentication_classes([TokenAuthentication])
def update_hostel(request, hostel_id):
    try:
        hostel = Hostel.objects.get(id=hostel_id)
    except Hostel.DoesNotExist:
        return Response({"error": "Hostel not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = HostelSerializer(hostel, data=request.data, partial=True)  # Use partial for PATCH
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
