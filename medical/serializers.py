from rest_framework import serializers
from .models import DiagnosisCase, DiagnosisVisit, Attachment


class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ['id', 'file', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']

class DiagnosisVisitSerializer(serializers.ModelSerializer):
    attachments = AttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = DiagnosisVisit
        fields = ['id', 'visit_date', 'notes', 'updated_at', 'attachments']
        read_only_fields = ['id', 'updated_at']

class DiagnosisCaseSerializer(serializers.ModelSerializer):
    visits = DiagnosisVisitSerializer(many=True, read_only=True)

    class Meta:
        model = DiagnosisCase
        fields = ['id', 'patient', 'title', 'created_at', 'visits']
        read_only_fields = ['id', 'created_at']

class DiagnosisCaseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model= DiagnosisCase
        fields=['id', 'patient', 'doctor', 'hospital', 'title', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate(self, attrs):
        if attrs['patient'].role != 'PATIENT':
            raise serializers.ValidationError("Selected user is not a patient.")
        if attrs['doctor'].role != 'DOCTOR':
            raise serializers.ValidationError("Selected user is not a doctor.")
        return attrs
    
class DiagnosisVisitCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiagnosisVisit
        fields = ['id', 'case', 'doctor', 'visit_date', 'notes', 'updated_at']
        read_only_fields = ['id', 'updated_at']

    def validate(self, attrs):
        if attrs['doctor'].role != 'DOCTOR':
            raise serializers.ValidationError("Selected user is not a doctor.")
        return attrs
