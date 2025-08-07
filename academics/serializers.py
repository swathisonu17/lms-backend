
from rest_framework import serializers
from .models import Attendance, Marks, QuizScore
from .models import Student
from .models import Quiz
from django.contrib.auth.models import User
from accounts.models import User
from .models import Faculty
from .models import Subject

print("DEBUG: Student =", Student)
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username']


class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer()  # show username from User model

    class Meta:
        model = Student
        fields = ['id', 'user', 'email', 'semester','usn']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['name'] = instance.user.username
        rep['usn'] = instance.usn
        return rep


class StudentRegisterSerializer(serializers.ModelSerializer):
    user = serializers.DictField()
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Student
        fields = ['user', 'email', 'semester', 'password']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        password = validated_data.pop('password')
        user = User.objects.create_user(username=user_data['username'], password=password)
        student = Student.objects.create(user=user, **validated_data)
        return student


# This serializer is used in your upload_bulk_attendance view to save data.
class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ['student','subject', 'status', 'date' ,'faculty']  # ✅ All writeable


class AttendanceDisplaySerializer(serializers.ModelSerializer):

    date = serializers.DateField(format="%d/%m/%Y")
    subject_name = serializers.CharField(source='subject', read_only=True)  # assuming subject is CharField
    student_name = serializers.CharField(source='student.user.username', read_only=True)
    usn = serializers.CharField(source='student.usn', read_only=True)  # ✅ Add this line

    class Meta:
        model = Attendance
        fields = ['student_name', 'usn','subject_name', 'status', 'date']


class MarksSerializer(serializers.ModelSerializer):
    subject = serializers.CharField(source='subject')
    assessment_type = serializers.SerializerMethodField()
    total_marks = serializers.IntegerField()
    marks = serializers.IntegerField()
    date = serializers.DateField(format="%d-%m-%Y")  # e.g., 29-07-2025

    class Meta:
        model = Marks
        fields = ['subject', 'assessment_type', 'total_marks', 'marks', 'date']
        read_only_fields = ['faculty']  # ✅ Prevent client from setting this manually

    def get_assessment_type(self, obj):
        return obj.get_assessment_type_display()


class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ['id', 'student', 'quiz_title', 'subject', 'marks', 'total_marks', 'date']
        read_only_fields = ['faculty']


class QuizScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizScore
        fields = ['student', 'quiz', 'marks']



# display quiz
class QuizDisplaySerializer(serializers.ModelSerializer):
    subject = serializers.CharField(source='subject.name', read_only=True)
    student = serializers.CharField(source='student.user.username', read_only=True)

    class Meta:
        model = Quiz
        fields = ['student', 'quiz_title', 'subject', 'marks', 'total_marks', 'date']



class FacultySerializer(serializers.ModelSerializer):
    class Meta:
        model = Faculty
        fields = '__all__'



class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name', 'semester']