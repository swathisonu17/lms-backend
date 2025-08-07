from reportlab.platypus import Table
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import TableStyle, SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .serializers import AttendanceSerializer, AttendanceDisplaySerializer, StudentRegisterSerializer
from .models import Attendance, Marks, Quiz, Student, Subject, QuizScore
from .serializers import AttendanceSerializer, StudentSerializer, MarksSerializer
from .serializers import QuizDisplaySerializer
from .models import Faculty
from .serializers import FacultySerializer
import csv
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.pdfmetrics import stringWidth
from .serializers import SubjectSerializer  # You must have this
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from django.http import HttpResponse
from .models import Quiz


# ✅ Fetch all subjects
def get_subjects(request):
    subjects = Subject.objects.all()
    data = [
        {"id": subj.id, "name": subj.name}
        for subj in subjects
    ]
    return JsonResponse(data, safe=False)

# ✅ Faculty uploads/view attendance
class AttendanceView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if hasattr(request.user, 'is_student') and request.user.is_student:
            attendance = Attendance.objects.filter(student=request.user)
        else:
            attendance = Attendance.objects.all()
        serializer = AttendanceSerializer(attendance, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AttendanceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ✅ Get students by semester
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_students_by_semester(request, sem):
    try:
        students = Student.objects.filter(semester=sem)
        data = [
            {
                "id": student.id,
                "name": student.user.username,
                "semester": student.semester,
                "usn": student.usn  # ✅ Include USN here
            }
            for student in students
        ]
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# ✅ Upload bulk attendance
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_bulk_attendance(request):
    data = request.data.get('attendance', [])
    if not isinstance(data, list):
        return Response({"error": "Attendance data must be a list."}, status=400)

    for record in data:
        print("▶ Incoming record:", record)  # 👈 ADD THIS
        record['faculty'] = request.user.id  # ✅ Inject the faculty
        serializer = AttendanceSerializer(data=record)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(serializer.errors, status=400)

    return Response({"message": "Attendance uploaded successfully."}, status=201)



class UploadMarksAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        print("Incoming data:", request.data)
        marks_data = request.data.get("marks", [])

        for entry in marks_data:
            student_id = entry.get("student")
            subject_id = entry.get("subject")  # subject ID from frontend
            marks = entry.get("marks")
            total_marks = entry.get("total_marks")
            date = entry.get("date")
            assessment_type = entry.get("assessment_type")

            if not all([student_id, subject_id, marks, total_marks, date, assessment_type]):
                return Response({"error": "All fields are required."}, status=400)

            try:
                student = Student.objects.get(id=student_id)
                subject_obj = Subject.objects.get(id=subject_id)
                subject_name = subject_obj.name  # ✅ Get subject name
            except Subject.DoesNotExist:
                return Response({"error": f"Subject with ID {subject_id} does not exist."}, status=404)
            except Student.DoesNotExist:
                return Response({"error": f"Student with ID {student_id} does not exist."}, status=404)

            Marks.objects.create(
                student=student,
                subject=subject_name,  # ✅ Store actual subject name
                marks=marks,
                total_marks=total_marks,
                date=date,
                assessment_type=assessment_type,
                faculty=request.user  # ✅ Set faculty
            )

        return Response({"message": "Marks uploaded successfully."})


# ✅ View student-specific attendance
class StudentAttendanceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            student = Student.objects.get(user=request.user)
        except Student.DoesNotExist:
            return Response({"error": "Student profile not found"}, status=404)

        attendance = Attendance.objects.filter(student=student).order_by('-date')
        # ✅ Use display serializer here
        serializer = AttendanceDisplaySerializer(attendance, many=True)
        return Response(serializer.data)

# ✅ View student-specific marks
class StudentMarksAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            student = request.user.academic_student
        except Student.DoesNotExist:
            return Response({"error": "Student profile not found."}, status=400)

        marks = Marks.objects.filter(student=student)
        data = [
            {   "usn": mark.student.usn,
                "subject": mark.subject,
                "assessment_type": mark.get_assessment_type_display(),
                "total_marks": mark.total_marks,
                "marks": mark.marks,
                "date": mark.date.strftime("%Y-%m-%d")
            }
            for mark in marks
        ]
        return Response(data)

class StudentListBySemesterView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        semester = request.GET.get("semester")
        if semester:
            students = Student.objects.filter(semester=semester)
        else:
            students = Student.objects.all()

        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data)


# ✅ View student marks using old serializer logic
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_marks(request):
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        return Response({"error": "Student not found"}, status=404)

    marks_qs = Marks.objects.filter(student=student)
    serializer = MarksSerializer(marks_qs, many=True)
    return Response(serializer.data)




@api_view(["POST"])
@permission_classes([IsAuthenticated])
def upload_quiz(request):
    data = request.data.get("quizzes", [])
    for entry in data:
        student_id = entry.get("student")
        quiz_title = entry.get("quiz_title")
        subject_id = entry.get("subject")
        marks = entry.get("marks")
        total_marks = entry.get("total_marks")
        date = entry.get("date")

        if not all([student_id, quiz_title, subject_id, marks, total_marks, date]):
            return Response({"error": "All fields are required."}, status=400)

        student = get_object_or_404(Student, id=student_id)
        subject = get_object_or_404(Subject, id=subject_id)

        Quiz.objects.create(
            student=student,
            quiz_title=quiz_title,
            subject=subject,
            marks=marks,
            total_marks=total_marks,
            date=date,
            faculty=request.user  # ✅ Set the logged-in faculty
        )

    return Response({"message": "Quiz marks uploaded successfully!"})

# viewing quiz
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_quiz(request):
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        return Response({"error": "Student profile not found."}, status=404)

    quizzes = Quiz.objects.filter(student=student).order_by('-date')
    serializer = QuizDisplaySerializer(quizzes, many=True)
    return Response(serializer.data)




class FacultyListView(APIView):
    def get(self, request):
        faculties = Faculty.objects.all()
        serializer = FacultySerializer(faculties, many=True)
        return Response(serializer.data)

class FacultyDetailView(APIView):
    def get(self, request, pk):
        try:
            faculty = Faculty.objects.get(pk=pk)
        except Faculty.DoesNotExist:
            return Response({'error': 'Faculty not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = FacultySerializer(faculty)
        return Response(serializer.data)

# ----------------------------
# ATTENDANCE EXPORT → csv
# ----------------------------

def export_attendance_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="attendance.csv"'

    writer = csv.writer(response)

    # ✅ Fix the missing comma between 'usn' and 'Subject'
    writer.writerow(['Student Username', 'USN', 'Subject', 'Date', 'Status'])

    attendances = Attendance.objects.filter(faculty=request.user)

    for record in attendances:
        writer.writerow([
            record.student.user.username,
            record.student.usn,
            record.subject,
            record.date.strftime('%d-%b-%Y'),
            record.status
        ])

    return response


# ----------------------------
# MARKS EXPORT → PDF
# ----------------------------

def export_marks_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="marks_report.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    title = Paragraph("Department of CSE - Marks Report", styles['Heading1'])
    elements.append(title)
    elements.append(Paragraph(" ", styles['Normal']))  # spacer

    # Table header
    data = [["Sl No", 'usn',"Student Email", "Semester", "Subject", "Assessment Type", "Marks Scored", "Total Marks", "Date"]]

    marks = Marks.objects.filter(faculty=request.user).select_related('student__user')  # ✅ only this faculty

    # Measure max width required for email column
    email_col_width = stringWidth("Student Email", 'Helvetica-Bold', 9)

    for idx, m in enumerate(marks, start=1):
        email_width = stringWidth(m.student.email, 'Helvetica', 9)
        email_col_width = max(email_col_width, email_width + 10)  # extra padding
        subject_style = ParagraphStyle(name='SubjectStyle', fontSize=9, wordWrap='CJK', leading=12)
        row = [
            idx,
            m.student.usn,
            m.student.email,
            f"Sem {m.student.semester}",
            m.subject,
            m.get_assessment_type_display(),
            m.marks,
            m.total_marks,
            m.date.strftime("%d-%m-%Y")
        ]
        data.append(row)

    table = Table(data, colWidths=[
        0.6 * inch,         # Sl No
        1.2 * inch,          #usn
        email_col_width,    # Email (dynamic)
        0.8 * inch,         # Semester
        1.0 * inch,         # Subject
        1.3 * inch,         # Assessment Type
        0.9 * inch,         # Marks Scored
        0.9 * inch,         # Total Marks
        1.0 * inch          # Date
    ])

    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#dce6f1")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.darkblue),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.whitesmoke]),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
    ]))

    elements.append(table)
    doc.build(elements)
    return response


# ----------------------------
# QUIZ EXPORT → CSV
# ----------------------------


def export_quiz_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="quiz_report.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()
    title = Paragraph("📘 <b>Quiz Report</b>", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))

    quizzes = Quiz.objects.filter(faculty=request.user).select_related('student__user', 'subject')

    data = [[
        "Sl No", "USN", "Student Email", "Semester", "Subject",
        "Marks Scored", "Total Marks", "Date"
    ]]

    email_style = ParagraphStyle(name='EmailStyle', fontSize=9, wordWrap='CJK', leading=12)
    subject_style = ParagraphStyle(name='SubjectStyle', fontSize=9, wordWrap='CJK', leading=12)

    for i, q in enumerate(quizzes, start=1):
        email_para = Paragraph(q.student.email, email_style)
        subject_para = Paragraph(q.subject.name, subject_style)

        data.append([
            i,
            q.student.usn,
            email_para,
            f"Sem {q.student.semester}",
            subject_para,
            q.marks,
            q.total_marks,
            q.date.strftime("%d-%m-%Y")
        ])

    # ✅ 8 column widths for 8 columns
    table = Table(data, colWidths=[
        0.6 * inch,    # Sl No
        1.2 * inch,    # USN
        2.2 * inch,    # Email
        0.8 * inch,    # Semester
        1.4 * inch,    # Subject
        0.9 * inch,    # Marks Scored
        0.9 * inch,    # Total Marks
        1.0 * inch     # Date
    ])

    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#006699")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.whitesmoke]),
    ]))

    elements.append(table)
    doc.build(elements)
    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_subjects_by_semester(request, semester):
    subjects = Subject.objects.filter(semester=semester)
    serializer = SubjectSerializer(subjects, many=True)
    return Response(serializer.data)



class StudentRegisterView(APIView):
    def post(self, request):
        serializer = StudentRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Student registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def register_user(request):
    data = request.data
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role")
    semester = data.get("semester")  # ✅ get semester from request

    if User.objects.filter(username=username).exists():
        return Response({"error": "Username already exists"}, status=400)

    user = User.objects.create_user(username=username, email=email, password=password)
    user.role = role
    user.save()

    if role == 'Student':
        Student.objects.create(user=user, email=email, semester=semester)  # ✅ save semester
    elif role == 'Faculty':
        Faculty.objects.create(user=user, email=email)

    return Response({"message": "User registered successfully"})