from django.db import models
from django.contrib.auth.models import AbstractUser

from config import settings
# Create your models here.

class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        PATIENT = "PATIENT", "Patient"
        DOCTOR = "DOCTOR", "Doctor"
        HOSPITAL = "HOSPITAL", "Hospital"
    role=models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.PATIENT,)
    def __str__(self):
        return f"{self.username} ({self.role})"

class PatientProfile(models.Model):
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),    
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]
    user=models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='patient_profile')
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES)
    weight = models.FloatField(help_text="Weight in kg")
    weight_measured_on = models.DateField()
    height = models.FloatField(help_text="Height in cm")
    date_of_birth = models.DateField()
    existing_conditions = models.TextField(blank=True, null=True)
    allergies = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile of {self.user.username}"
