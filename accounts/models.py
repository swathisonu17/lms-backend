# from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
# from django.contrib.auth.models import AbstractUser, Group, Permission, PermissionsMixin
# from django.db import models
# from django.conf import settings
#
#
# class UserManager(BaseUserManager):
#     def create_user(self, email, password=None, **extra_fields):
#         if not email:
#             raise ValueError("Users must have an email address")
#         email = self.normalize_email(email)
#         user = self.model(email=email, **extra_fields)
#         user.set_password(password)
#         user.save(using=self._db)
#         return user
#
#     def create_superuser(self, email, password, **extra_fields):
#         extra_fields.setdefault("is_staff", True)
#         extra_fields.setdefault("is_superuser", True)
#         return self.create_user(email, password, **extra_fields)
#
# class User(AbstractBaseUser, PermissionsMixin):
#     email = models.EmailField(unique=True)
#     username = models.CharField(max_length=150, blank=True)  # optional
#     is_active = models.BooleanField(default=False)
#     is_staff = models.BooleanField(default=False)
#     is_student = models.BooleanField(default=False)
#     is_faculty = models.BooleanField(default=False)
#
#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = []
#
#     objects = UserManager()
#
# class Student(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     # user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="academic_student")
#     email = models.EmailField(unique=True)
#     semester = models.IntegerField()
#     usn = models.CharField(max_length=20, unique=True, null=True, blank=True)  # ✅ Add this line
#     def __str__(self):
#         return self.user.username
#
#
# class Faculty(models.Model):
#     user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     email = models.EmailField(unique=True)
#
#     def __str__(self):
#         return self.email




from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.conf import settings


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)

        # Prevent accidental dual roles
        extra_fields.setdefault('is_student', False)
        extra_fields.setdefault('is_faculty', False)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, blank=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)
    is_faculty = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField(unique=True)
    semester = models.IntegerField()
    usn = models.CharField(max_length=20, unique=True, null=True, blank=True)

    def __str__(self):
        return self.user.username or self.email


class Faculty(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.email
