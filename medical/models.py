from django.db import models
from django.conf import settings

from users.models import Doctor, Hospital

# Create your models here.

class DiagnosisCase(models.Model):
    patient=models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='diagnosis_cases')
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,null=True, related_name='diagnosis_cases_as_doctor')
    hospital = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

def __str__(self):
      return f"{self.title} - {self.patient.username}"

class DiagnosisVisit(models.Model):
    case = models.ForeignKey(DiagnosisCase, on_delete=models.CASCADE, related_name='visits')
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='diagnosis_visits')
    visit_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    medications = models.JSONField(default=list, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Visit on {self.visit_date} for {self.case.title}"
    
class Attachment(models.Model):
    visit = models.ForeignKey(DiagnosisVisit, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attachment for {self.visit.case.title} on {self.uploaded_at}"
    

class AssignedDoctor(models.Model):
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name="assignments")
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="assigned_doctors")
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="assigned_patients")
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('patient', 'doctor')  # Prevent multiple duplicate links

    def __str__(self):
        return f"{self.doctor.user.username} assigned to {self.patient.username}"
    
# medical/models.py

class ScheduledVisit(models.Model):
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="scheduled_visits")
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="scheduled_patients")
    diagnosis_case = models.ForeignKey("DiagnosisCase", on_delete=models.CASCADE, related_name="scheduled_visits")
    visit_date = models.DateTimeField()
    visit_time = models.TimeField()
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Visit for {self.patient.username} with {self.doctor.user.username} on {self.visit_date}"
