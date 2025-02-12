from rest_framework.response import Response
from rest_framework import status
def validate_required_fields(data, fields):
    """
    Validate that all required fields are present in the request data.
    """
    missing_fields = [field for field in fields if not data.get(field)]
    if missing_fields:
        return Response({'error': f"{', '.join(missing_fields)} are required", 'status': False}, status=status.HTTP_400_BAD_REQUEST)
    return None
