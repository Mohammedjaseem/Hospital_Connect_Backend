from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.response import Response
from rest_framework import status
from .models import CustomUser, OTP
from .serializers import RegisterUserSerializer, CustomUserSerializer
from .tasks import send_otp_to_email
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from utils.validate_required_fields import validate_required_fields
import logging
from django.db import transaction
from staff.models import StaffProfile
from django_tenants.utils import schema_context
from staff.serializers import StaffProfileSerializer
# from students.serializers import StudentProfileSerializer
from utils.handle_exception import handle_exception
from app.models import Organizations
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from django.utils.http import http_date
from datetime import timedelta, datetime
from hostel.models import Hostel


logger = logging.getLogger(__name__)
# Create your views here.
@api_view(['POST'])
def register_user(request):
    """
    Register a new user. Validates required fields, checks password constraints,
    and sends an OTP to the user's email upon successful registration.
    """
    required_fields = ['password', 'confirm_password', 'email', 'org','name']
    validation_response = validate_required_fields(request.data, required_fields)
    if validation_response:
        return validation_response

    password = request.data.get('password')
    confirm_password = request.data.get('confirm_password')
    email = request.data.get('email')
    name = request.data.get('name')
    org = request.data.get('org')

    if password != confirm_password:
        return Response({'error': 'Passwords do not match', 'status': False}, status=status.HTTP_400_BAD_REQUEST)
    if len(password) < 6:
        return Response({'error': 'Password must be at least 6 characters long', 'status': False}, status=status.HTTP_400_BAD_REQUEST)
    if CustomUser.objects.filter(email=email).exists():
        return Response({'error': 'User with this email already exists', 'status': False}, status=status.HTTP_400_BAD_REQUEST)

    serializer = RegisterUserSerializer(data=request.data)
    try:
        org_instance = Organizations.objects.get(pk=org)
        with transaction.atomic():
            serializer.is_valid(raise_exception=True)
            user, otp = serializer.save()
            print("otp : ",otp)
            send_otp_to_email.delay(user.email, otp,name,org_instance.name,source="verify your email address")  # Send OTP to user's email using Celery
        return Response({'message': 'User created successfully', 'uuid': user.uuid, 'status': True}, status=status.HTTP_201_CREATED)
    except Exception as e:
        logger.error(f"Error during user registration: {e}")
        return Response({'error': 'Unexpected error occurred, Please try again later', 'status': False}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@throttle_classes([AnonRateThrottle]) 
def verify_otp(request):
    """
    Verify the OTP sent to the user's email. Marks the user as verified if the OTP is valid.
    """
    

    validation_response = validate_required_fields(request.data, ['otp', 'uuid','source'])
    if validation_response:
        return validation_response
    
    otp = request.data.get('otp')
    uuid = request.data.get('uuid')
    source = request.data.get('source') # Source can be either 'register' or 'forgot_password'

    try:
        user = get_object_or_404(CustomUser, uuid=uuid)
        otp_instance = OTP.objects.filter(user=user).order_by('-created_at').first()  # Get the latest OTP

        if not otp_instance or otp_instance.is_expired() or not otp_instance.verify_otp(otp):
            return Response({'error': 'Invalid or expired OTP', 'status': False}, status=status.HTTP_400_BAD_REQUEST)

        user.is_verified = True
        user.save()
        if source == 'forgot_password':
            otp_instance.is_verified = True
            otp_instance.save()
        else:
            otp_instance.delete()
        return Response({'message': 'User verified successfully', 'status': True}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error verifying OTP: {e}")
        return Response({'error': 'An unexpected error occurred. Please try again later.', 'status': False}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def resend_otp(request):
    """
    Resend a new OTP to the user's email.
    """

    validation_response = validate_required_fields(request.data, ['uuid'])
    if validation_response:
        return validation_response
    
    uuid = request.data.get('uuid')
    org = request.data.get('org')
    source = request.data.get('source')  # Source can be either 'register' or 'forgot_password'

    try:
        org_instance = Organizations.objects.get(pk=org)
        user = get_object_or_404(CustomUser, uuid=uuid)
        otp = RegisterUserSerializer.generate_otp()
        print("otp : ",otp)
        otp_instance = OTP(user=user)
        otp_instance.set_otp(str(otp))
        otp_instance.save()
        send_otp_to_email.delay(user.email, otp,user.name,org_instance.name,source=source)  # Send new OTP to user's email using celery

        return Response({'message': 'New OTP sent successfully', 'status': True}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error resending OTP: {e}")
        return Response({'error': 'An unexpected error occurred. Please try again later.', 'status': False}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    


@throttle_classes([AnonRateThrottle])
@api_view(['POST'])
def login(request):
    """
    Authenticate a user and return JWT tokens in the response body.
    """
    # Validate required fields
    validation_response = validate_required_fields(request.data, ['email', 'password'])
    if validation_response:
        return validation_response

    email = request.data.get('email')
    password = request.data.get('password')
    org = request.data.get('org')

    try:
        # Authenticate the user
        user = authenticate(email=email, password=password)
        if not user:
            return Response({'error': 'Invalid email or password', 'status': False}, status=status.HTTP_400_BAD_REQUEST)

        # # Uncomment this if organization-based authentication is needed
        # if user.org.id != org:
        #     return Response({'error': 'You do not belong to this hospital', 'status': False}, status=status.HTTP_400_BAD_REQUEST)

        # Handle unverified user
        if not user.is_verified:
            otp = RegisterUserSerializer.generate_otp()
            otp_instance = OTP.objects.create(user=user)
            otp_instance.set_otp(str(otp))
            otp_instance.save()
            send_otp_to_email.delay(user.email, otp, user.name, user.org.name,source="verify your email address")  # Send OTP using Celery
            return Response({
                'message': 'User is not verified. Please verify your OTP.',
                'uuid': user.uuid,
                'is_email_verified': False,
                'status': False
            }, status=status.HTTP_200_OK)

        # Initialize response variables
        staff_profile = None
        is_profile_created = False
        is_hostel_incharge = False
        hostel_name = None

        # Handle tenant-specific data
        with schema_context(user.org.client.schema_name):  # Switch to tenant schema
            staff_profile = StaffProfile.objects.filter(user=user).select_related("department", "designation").first()

            is_profile_created = bool(staff_profile)  # True if profile exists, else False
            is_hostel_incharge = (
                Hostel.objects.filter(incharge=staff_profile).exists()
                if staff_profile else False
            )
            is_warden = Hostel.objects.filter(wardens=staff_profile).exists() if staff_profile else False
            hostel_name = staff_profile.hostel.name if staff_profile and staff_profile.hostel else None


        # Generate JWT tokens
        token = RefreshToken.for_user(user)
        access_token = str(token.access_token)
        refresh_token = str(token)

        # # Serialize user details
        user_serializer = CustomUserSerializer(user)
        staff_profile_serializer = StaffProfileSerializer(staff_profile, context={'request': request}).data if staff_profile else None
    
        # student_profile_serializer = StudentLoginSerializer(student_profile) if student_profile else None
        # enrolled_student_data = {
        #     'class': enrolled_student.classs if enrolled_student else None,
        #     'division': enrolled_student.division if enrolled_student else None,
        #     'academic_year': enrolled_student.academic_year if enrolled_student else None
        # } if enrolled_student else None

        # # Merge student profile data and enrollment data
        # if student_profile_serializer:
        #     student_profile_data = {
        #         **student_profile_serializer.data,
        #         **(enrolled_student_data or {})
        #     }
        # else:
        #     student_profile_data = None

        # Return tokens and user profile data in response body
        if staff_profile_serializer:
            staff_profile_serializer['is_hostel_incharge'] = is_hostel_incharge
            staff_profile_serializer['is_warden'] = is_warden
            staff_profile_serializer['hostel_name'] = hostel_name

            

        return Response({
            'message': "Login Successful",
            'status': True,
            'user': user_serializer.data,
            'is_profile_created': is_profile_created,
            'staff_profile': staff_profile_serializer if staff_profile else None,
            # 'student_profile': student_profile_data,
            'access': access_token,
            'refresh': refresh_token
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error during user login: {e}")
        return Response({'error': 'An unexpected error occurred', 'status': False}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@throttle_classes([AnonRateThrottle])
def refresh_token(request):
    '''
    Refresh the access token using the refresh token sent in the request body.
    '''
    try:
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'error': 'Refresh token not provided.', 'status': False}, status=status.HTTP_400_BAD_REQUEST)

        # Generate new access token
        token = RefreshToken(refresh_token)
        access_token = str(token.access_token)

        return Response({
            'message': "Token refreshed successfully",
            'status': True,
            'access': access_token
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error refreshing token: {e}")
        return Response({'error': 'Invalid or expired refresh token.', 'status': False}, status=status.HTTP_401_UNAUTHORIZED)
    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    '''
    Logout the user by blacklisting the refresh token.
    '''
    validation_response = validate_required_fields(request.data, ['refresh'])
    if validation_response:
        return validation_response
    try:
        refresh_token = request.data.get('refresh')
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'message': 'Logout successful', 'status': True}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error during logout: {e}")
        return Response({'error': 'An unexpected error occurred. Please try again later.', 'status': False}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def home(request):

    """
    Return a welcome message for authenticated users.
    """
    # Access the current authenticated user
    current_user = request.user
    
    # Access the tenant information
    current_tenant = request.tenant  # Assuming you have set up tenant middleware correctly

    # Prepare the response message
    return Response({'message': f'Welcome {current_user} to {current_tenant} School Connect', 'status': True}, status=status.HTTP_200_OK)


@api_view(['POST'])
def forgot_password(request):
    """
    Handle forgot password functionality by sending an OTP to the user's email.
    """
    
    validation_response = validate_required_fields(request.data, ['email'])
    if validation_response:
        return validation_response
    
    email = request.data.get('email')

    try:
        user = CustomUser.objects.filter(email=email).first()
        if not user:
            return Response({'error': 'User with this email does not exist', 'status': False}, status=status.HTTP_400_BAD_REQUEST)

        otp = RegisterUserSerializer.generate_otp()
        otp_instance = OTP.objects.create(user=user)
        otp_instance.set_otp(str(otp))
        otp_instance.save()
        send_otp_to_email.delay(user.email, otp,user.name, user.org.name,source="reset your password")  # Send OTP to user's email using celery
        return Response({'message': 'OTP sent successfully','uuid':user.uuid,'status': True}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error during forgot password process: {e}")
        return Response({'error': 'An unexpected error occurred. Please try again later.', 'status': False}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['POST'])
def reset_password(request):
    '''
    Reset password using OTP sent to the user's email. 
    '''
    
    validation_response = validate_required_fields(request.data, ['uuid', 'password', 'confirm_password', 'otp'])
    if validation_response:
        return validation_response
    
    uuid = request.data.get('uuid')
    password = request.data.get('password')
    confirm_password = request.data.get('confirm_password')
    otp = request.data.get('otp')

    if password != confirm_password:
        return Response({'error': 'Passwords do not match', 'status': False}, status=status.HTTP_400_BAD_REQUEST)
    if len(password) < 6:
        return Response({'error': 'Password must be at least 6 characters long', 'status': False}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = CustomUser.objects.filter(uuid=uuid).first()
        if not user:
            return Response({'error': 'User does not exist', 'status': False}, status=status.HTTP_404_NOT_FOUND)
        
        otp_instance = OTP.objects.filter(user=user).order_by('-created_at').first()
        if not otp_instance:
            return Response({'error': 'OTP not found', 'status': False}, status=status.HTTP_400_BAD_REQUEST)
        if otp_instance.is_expired():
            return Response({'error': 'OTP has expired', 'status': False}, status=status.HTTP_400_BAD_REQUEST)
        if not otp_instance.verify_otp(otp):
            return Response({'error': 'Invalid OTP', 'status': False}, status=status.HTTP_400_BAD_REQUEST)
        if not otp_instance.is_verified:
            return Response({'error': 'OTP not verified', 'status': False}, status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(password)
        user.save()
        otp_instance.delete()
        return Response({'message': 'Password reset successfully', 'status': True}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error resetting password: {e}")
        return Response({'error': 'An unexpected error occurred. Please try again later.', 'status': False}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_retrival(request):
    """
    Retrieve user details including staff or student profile for the authenticated user.
    """
    try:
        user = request.user

        # Initialize response variables
        staff_profile, student_profile, enrolled_student = None, None, None
        is_profile_created = False
        is_hostel_incharge = False
        is_warden = False
        hostel_name = None

        # Handle tenant-specific data
        with schema_context(user.org.client.schema_name):  # Switch to tenant schema
            staff_profile = StaffProfile.objects.filter(user=user).select_related("department", "designation").first()

            is_profile_created = bool(staff_profile)  # True if profile exists, else False
            is_hostel_incharge = (
                Hostel.objects.filter(incharge=staff_profile).exists()
                if staff_profile else False
            )
            is_warden = Hostel.objects.filter(wardens=staff_profile).exists() if staff_profile else False
            hostel_name = staff_profile.hostel.name if staff_profile and staff_profile.hostel else None

        # Serialize user details
        user_serializer = CustomUserSerializer(user)
        staff_profile_serializer = StaffProfileSerializer(staff_profile, context={'request': request}).data if staff_profile else None
        # student_profile_serializer = StudentLoginSerializer(student_profile) if student_profile else None
        # enrolled_student_data = {
        #     'class': enrolled_student.classs if enrolled_student else None,
        #     'division': enrolled_student.division if enrolled_student else None,
        #     'academic_year': enrolled_student.academic_year if enrolled_student else None,
        #     # 'classroom': enrolled_student.classroom if enrolled_student else None
        # } if enrolled_student else None

        # Merge student profile data and enrollment data
        # if student_profile_serializer:
        #     student_profile_data = {
        #         **student_profile_serializer.data,
        #         **(enrolled_student_data or {})
        #     }
        # else:
        #     student_profile_data = None

        # Return response
        if staff_profile_serializer:
            staff_profile_serializer['is_hostel_incharge'] = is_hostel_incharge
            staff_profile_serializer['is_warden'] = is_warden
            staff_profile_serializer['hostel_name'] = hostel_name
        return Response({
            'message': "User retrieved successfully",
            'is_profile_created': is_profile_created,
            'user': user_serializer.data,
            'staff_profile': staff_profile_serializer if staff_profile else None,
            'is_hostel_incharge': is_hostel_incharge,
            # 'student_profile': student_profile_data,
            'status': True
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return handle_exception(e)