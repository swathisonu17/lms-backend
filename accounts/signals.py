# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.contrib.auth.models import User
# from .models import FacultyProfile
#
# @receiver(post_save, sender=User)
# def create_faculty_profile(sender, instance, created, **kwargs):
#     if created and instance.is_staff:  # assuming faculty = staff
#         FacultyProfile.objects.create(user=instance)
#
# @receiver(post_save, sender=User)
# def save_faculty_profile(sender, instance, **kwargs):
#     if hasattr(instance, 'faculty_profile'):
#         instance.faculty_profile.save()
