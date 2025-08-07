# lms_backend/views.py
from django.http import JsonResponse

def root_api(request):
    return JsonResponse({"message": "LMS Backend API Running"})
