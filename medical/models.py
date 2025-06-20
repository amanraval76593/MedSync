from django.db import models
from django.conf import settings

# Create your models here.

class DiagnosisCase(models.Model):
    patient=models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='diagnosis_cases')
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,null=True, related_name='diagnosis_cases_as_doctor')
    hospital = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

def __str__(self):
      return f"{self.title} - {self.patient.username}"

class DiagnosisVisit(models.Model):
    case = models.ForeignKey(DiagnosisCase, on_delete=models.CASCADE, related_name='visits')
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='diagnosis_visits')
    visit_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Visit on {self.visit_date} for {self.case.title}"
    
class Attachment(models.Model):
    visit = models.ForeignKey(DiagnosisVisit, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attachment for {self.visit.case.title} on {self.uploaded_at}"