from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings
from django.core.mail import send_mail

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers as drf_serializers

from . import serializers as local_serializers
from .models import Student, Faculty
from .utils import send_verification_email

User = get_user_model()


class RegisterView(APIView):
    def post(self, request):
        serializer = local_serializers.RegisterSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.save()
            user.is_active = True
            user.save()
            send_verification_email(user, request)
            return Response({'message': 'Registration successful. Please verify your email.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=400)


@api_view(['POST'])
def register(request):
    serializer = local_serializers.RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        user.is_active = True
        user.save()
        return Response({'message': 'Registration successful. Please verify your email.'})
    return Response(serializer.errors, status=400)


class VerifyEmail(APIView):
    def get(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
            if default_token_generator.check_token(user, token):
                user.is_active = True
                user.save()
                return Response({'message': 'Email verified successfully'}, status=200)
            else:
                return Response({'error': 'Invalid token'}, status=400)
        except Exception:
            return Response({'error': 'Verification failed'}, status=400)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        user = User.objects.filter(email=email).first()

        if user:
            if not user.check_password(password):
                raise drf_serializers.ValidationError("Invalid password.")
            if not user.is_active:
                raise drf_serializers.ValidationError("Account is not verified.")
            attrs['username'] = user.username
            data = super().validate(attrs)
            data['role'] = "faculty" if user.is_faculty else "student"
            data['email'] = user.email
            data['username'] = user.username
            return data

        raise drf_serializers.ValidationError("Invalid email or password.")


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        return Response({
            "username": user.username,
            "email": user.email,
            "is_faculty": getattr(user, "is_faculty", False),
            "is_student": getattr(user, "is_student", False),
        })


class ForgotPasswordView(APIView):
    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=404)

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_link = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"

        send_mail(
            "Reset Your Password",
            f"Click the link to reset your password:\n\n{reset_link}",
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        return Response({"message": "Password reset link sent."})


class ResetPasswordView(APIView):
    def post(self, request):
        uidb64 = request.data.get('uid')
        token = request.data.get('token')
        password = request.data.get('password')

        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({'error': 'Invalid user ID'}, status=status.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(user, token):
            return Response({'error': 'Invalid or expired token.'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(password)
        user.save()
        return Response({'message': 'Password reset successful!'}, status=status.HTTP_200_OK)
