from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


# ---------------------------
# Student Model
# ---------------------------
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="academic_student")
    email = models.EmailField(unique=True)
    semester = models.IntegerField()
    usn = models.CharField(max_length=20, unique=True, null=True, blank=True)
    def __str__(self):
        return self.user.username

# ---------------------------
# Attendance Model
# ---------------------------
class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, default="Unknown")  # ✅ add default
    date = models.DateField()
    status = models.CharField(max_length=10, choices=[("Present", "Present"), ("Absent", "Absent")])

    # ✅ Safely added with null=True and blank=True
    faculty = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.subject} - {self.status}"

# ---------------------------
# Subject Model
# ---------------------------
class Subject(models.Model):
    name = models.CharField(max_length=100)
    semester = models.PositiveIntegerField(null=True, blank=True)
    def __str__(self):
        return self.name

# ---------------------------
# AssessmentType Model
# ---------------------------
class AssessmentType(models.Model):
    name = models.CharField(max_length=50)  # e.g., Midterm, Final

    def __str__(self):
        return self.name

# ---------------------------
# Marks Model
# ---------------------------
class Marks(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    assessment_type = models.CharField(max_length=50, choices=[
        ('unit', 'Unit Test'),
        ('quiz', 'Quiz'),
        ('midterm', 'Midterm'),
        ('assignment', 'Assignment'),
        ('final', 'Final Exam')
    ])
    marks = models.IntegerField(default=0)
    total_marks = models.IntegerField(default=100)
    date = models.DateField()
    faculty = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # ✅ new

    def __str__(self):
        return f"{self.student.user.username} - {self.assessment_type} - {self.subject}"

# ---------------------------
# Quiz Model
# ---------------------------
class Quiz(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    quiz_title = models.CharField(max_length=100)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, default=1)  # Set default to Python
    marks = models.IntegerField()
    total_marks = models.IntegerField()
    date = models.DateField()
    faculty = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # ✅ Add this

    def __str__(self):
        return f"{self.student} - {self.quiz_title}"


# Links each student to a quiz with their score.
class QuizScore(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='scores')
    marks = models.IntegerField()

    def __str__(self):
        return f"{self.student.user.username} - {self.quiz.title} - {self.marks}"



class Faculty(models.Model):
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    contact = models.CharField(max_length=15)
    experience = models.PositiveIntegerField()
    photo = models.ImageField(upload_to='faculty_photos/')

    def __str__(self):
        return self.name
