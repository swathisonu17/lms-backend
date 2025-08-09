from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import Student, Faculty

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    role = serializers.ChoiceField(choices=[('Student', 'Student'), ('Faculty', 'Faculty')])

    semester = serializers.IntegerField(required=False, allow_null=True)
    usn = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'role', 'semester', 'usn']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        validate_password(attrs['password'])

        role = attrs.get('role')
        if role == 'Student':
            semester = attrs.get('semester')
            usn = attrs.get('usn')

            if semester in [None, '']:
                raise serializers.ValidationError({"semester": "Semester is required for students."})
            if usn in [None, '']:
                raise serializers.ValidationError({"usn": "USN is required for students."})

        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        role = validated_data.pop('role', None)

        # Clean semester and usn, default to None if not given or empty
        semester = validated_data.pop('semester', None)
        if semester == '':
            semester = None
        usn = validated_data.pop('usn', None)
        if usn == '':
            usn = None

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )

        if role and role.lower() == 'student':
            user.is_student = True
            user.is_faculty = False
            user.save()
            Student.objects.create(user=user, email=user.email, semester=semester, usn=usn)

        elif role and role.lower() == 'faculty':
            user.is_faculty = True
            user.is_student = False
            user.save()
            Faculty.objects.create(user=user, email=user.email)

        return user


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'user', 'email', 'semester', 'usn']
