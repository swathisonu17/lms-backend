from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import Student
from rest_framework import serializers
from .models import Student
User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    role = serializers.ChoiceField(choices=[('Student', 'Student'), ('Faculty', 'Faculty')])  # ✅ Add role field

    class Meta:
        model = User
        # fields = ['username', 'email', 'password', 'password2']
        fields = ['username', 'email', 'password', 'password2', 'role']  # ✅ Include role
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        validate_password(attrs['password'])
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        role = self.context['request'].data.get('role')# Get role from the request
        semester = validated_data.pop('semester', None)  # Only for students
        usn = self.context['request'].data.get('usn')  # ✅ Add this line

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            # role=validated_data['role']  # ✅ Save role in User model
        )
        # Set role flags
        if role == 'student':
            user.is_student = True
            user.save()
            # ✅ Create student profile
            from .models import Student
            Student.objects.create(user=user, email=user.email, semester=semester,usn=usn)

        elif role == 'faculty':
            user.is_faculty = True
            user.save()
            # ✅ Create faculty profile
            from .models import Faculty
            Faculty.objects.create(user=user, email=user.email)
        user.save()
        return user

class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'user', 'email', 'semester', 'usn']