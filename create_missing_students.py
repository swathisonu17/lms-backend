import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms_backend.settings')
django.setup()

from accounts.models import User
from academics.models import Student

# Get existing student usernames
existing_students = set(Student.objects.values_list('user__username', flat=True))

# Loop through users and attach Student profile if missing
for i in range(1, 11):
    username = f"student{i}"
    email = f"{username}@example.com"
    semester = (i % 5) + 1

    try:
        user = User.objects.get(username=username)
        if username not in existing_students:
            Student.objects.create(user=user, email=email, semester=semester)
            print(f"✅ Created Student profile for {username}")
        else:
            print(f"⚠️ Student profile for {username} already exists.")
    except User.DoesNotExist:
        print(f"❌ User {username} not found. Skipping.")
