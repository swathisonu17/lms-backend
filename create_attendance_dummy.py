from django.contrib.auth.models import User
from academics.models import Student, Attendance
from datetime import date
import random

# Dummy data
dummy_users = [
    {"username": "student1", "email": "student1@example.com"},
    {"username": "student2", "email": "student2@example.com"},
    {"username": "student3", "email": "student3@example.com"},
]

for u in dummy_users:
    username = u["username"]
    email = u["email"]

    user, created = User.objects.get_or_create(username=username, email=email)
    if created:
        user.set_password("password123")
        user.save()

    student, _ = Student.objects.get_or_create(user=user, defaults={
        "usn": f"1CS{random.randint(10, 99)}0{random.randint(10, 99)}",
        "semester": random.choice([3, 5, 7])
    })

    Attendance.objects.get_or_create(
        student=student,
        date=date.today(),
        defaults={"status": random.choice(["Present", "Absent"])}
    )

    print(f"✅ Created {username} with attendance.")
