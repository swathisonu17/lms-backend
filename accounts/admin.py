from django.contrib import admin
from .models import Student

# Register your models here.

admin.site.register(Student)


class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'is_faculty', 'is_student', 'is_active')
    list_filter = ('is_faculty', 'is_student', 'is_active')
    search_fields = ('email', 'username')