from django.urls import path
from .views import get_students_by_semester
from .views import upload_bulk_attendance
from .views import UploadMarksAPIView
from .views import StudentListBySemesterView
from .views import StudentMarksAPIView
from .views import StudentAttendanceView
from .views import get_subjects
from .views import view_quiz
from .views import FacultyListView, FacultyDetailView
from .views import upload_quiz, export_attendance_csv
from .views import export_marks_pdf
from .views import export_quiz_pdf
from .views import get_subjects_by_semester
from .views import StudentRegisterView


urlpatterns = [
    # path('courses/', CourseListView.as_view(), name='course_list'),
    path('students/<int:sem>/', get_students_by_semester),
    path('upload-bulk-attendance/', upload_bulk_attendance),
    path('upload-attendance/', upload_bulk_attendance, name='upload-attendance'),
    path("students/", StudentListBySemesterView.as_view(), name="students-by-semester"),
    path('upload-marks/', UploadMarksAPIView.as_view(), name='upload-marks'),
    path('upload-quiz/', upload_quiz, name='upload-quiz'),
    path('student/marks/', StudentMarksAPIView.as_view() , name='student-marks'),
    path('student/view-attendance/', StudentAttendanceView.as_view(), name='student-view-attendance'),
    path("subjects/", get_subjects, name="get-subjects"),
    path('student/view-quiz/', view_quiz, name='view-quiz'),
    path('faculties/', FacultyListView.as_view(), name='faculty-list'),
    path('faculties/<int:pk>/', FacultyDetailView.as_view(), name='faculty-detail'),
    path('export-attendance/', export_attendance_csv, name='export-attendance'),
    path("export-marks/", export_marks_pdf, name="export-marks"),
    path("export-quiz/", export_quiz_pdf, name="export-quiz"),
    path("subjects/<int:semester>/", get_subjects_by_semester),
    path('student-register/', StudentRegisterView.as_view(), name='student-register'),
]