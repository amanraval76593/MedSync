from datetime import datetime, timedelta
import cloudinary.uploader
from rest_framework import serializers
from django.utils import timezone
from .tasks import send_visit_reminder
from users.models import CustomUser, Doctor
from .models import AssignedDoctor, DiagnosisCase, DiagnosisVisit, Attachment, ScheduledVisit, VisitDocument
from .cloudinary_config import cloudinary
from cloudinary.utils import cloudinary_url

# import cloudinary.uploader



class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ['id', 'file', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']

class VisitDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model=VisitDocument
        fields = ['id', 'document_type', 'file_url', 'uploaded_at']
        read_only_fields = ['id', 'updated_at']
class DiagnosisVisitSerializer(serializers.ModelSerializer):
    documents=VisitDocumentSerializer(many=True, read_only=True)
    doctor_name=serializers.SerializerMethodField()

    class Meta:
        model = DiagnosisVisit
        fields = ['id', 'visit_date', 'notes', 'updated_at', 'attachments','doctor_name','medications','documents']
        read_only_fields = ['id', 'updated_at']
    def get_doctor_name(self, obj):
        return obj.doctor.get_full_name() if obj.doctor else None

class DiagnosisCaseSerializer(serializers.ModelSerializer):
    visits = DiagnosisVisitSerializer(many=True, read_only=True)

    class Meta:
        model = DiagnosisCase
        fields = ['id', 'patient', 'title', 'created_at', 'visits']
        read_only_fields = ['id', 'created_at']

class DiagnosisCaseWithVisitsSerializer(serializers.ModelSerializer):
    visits = DiagnosisVisitSerializer(many=True, read_only=True)  # uses related_name='visits'

    class Meta:
        model = DiagnosisCase
        fields = ['id', 'title', 'created_at', 'doctor', 'hospital', 'visits']

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

    # def validate(self, attrs):
       
    #     if attrs['doctor'].role != 'DOCTOR':
    #         raise serializers.ValidationError("Selected user is not a doctor.")
    #     return attrs
class DiagnosisCaseDetailSerializer(serializers.ModelSerializer):
    visits = DiagnosisVisitSerializer(many=True, read_only=True)
    doctor_name = serializers.SerializerMethodField()

    class Meta:
        model = DiagnosisCase
        fields = ['id', 'patient', 'doctor', 'hospital', 'title', 'created_at', 'visits', 'doctor_name']

    def get_doctor_name(self, obj):
        doctor = obj.doctor 
        # doctor=Doctor.objects.get(id=doctor_id)
        print(doctor) 
        if doctor: 
            return f"{doctor.first_name} {doctor.last_name}"
        return None



class AssignDoctorSerializer(serializers.Serializer):
    patient_username = serializers.CharField()
    doctor_username = serializers.CharField()

    def validate(self, data):
        from users.models import CustomUser
        from medical.models import Doctor

        try:
            patient = CustomUser.objects.get(username=data['patient_username'], role=CustomUser.Role.PATIENT)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("Patient not found.")

        try:
            doctor_user = CustomUser.objects.get(username=data['doctor_username'], role=CustomUser.Role.DOCTOR)
            doctor = doctor_user.doctor_profile
        except (CustomUser.DoesNotExist, Doctor.DoesNotExist):
            raise serializers.ValidationError("Doctor not found or profile missing.")

        data['patient'] = patient
        data['doctor'] = doctor
        return data
    
class AssignedPatientSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='patient.username')
    email = serializers.EmailField(source='patient.email')
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = AssignedDoctor
        fields = ['username', 'email', 'full_name', 'assigned_at']

    def get_full_name(self, obj):
        user = obj.patient
        return f"{user.first_name} {user.last_name}"
    
class DiagnosisCaseSummarySerializer(serializers.ModelSerializer):
    doctor = serializers.SerializerMethodField()
    visits = DiagnosisVisitSerializer(many=True, read_only=True)

    class Meta:
        model = DiagnosisCase
        fields = ['id', 'title', 'doctor', 'hospital','description', 'created_at', 'visits']

    def get_doctor(self, obj):
        return f"{obj.doctor.first_name} {obj.doctor.last_name}" if obj.doctor else None
    
# medical/serializers.py

class CreateDiagnosisCaseSerializer(serializers.ModelSerializer):
    patient_username = serializers.CharField(write_only=True)

    class Meta:
        model = DiagnosisCase
        fields = ['title', 'hospital','description', 'patient_username']

    def create(self, validated_data):
        request = self.context['request']
        doctor_user = request.user
        patient_username = validated_data.pop('patient_username')

        # Get patient object
        try:
            patient = CustomUser.objects.get(username=patient_username, role=CustomUser.Role.PATIENT)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("Patient not found.")

        # Ensure doctor is assigned to patient
        try:
            doctor_profile = doctor_user.doctor_profile
        except:
            raise serializers.ValidationError("Doctor profile not found.")

        if not AssignedDoctor.objects.filter(doctor=doctor_profile, patient=patient).exists():
            raise serializers.ValidationError("You are not assigned to this patient.")

        # Create diagnosis
        return DiagnosisCase.objects.create(
            patient=patient,
            doctor=doctor_user,
            **validated_data
        )
    


class DoctorDiagnosisVisitCreateSerializer(serializers.ModelSerializer):
    case_id = serializers.IntegerField(write_only=True)
    medications = serializers.JSONField(required=False)

    class Meta:
        model = DiagnosisVisit
        fields = ['case_id', 'notes', 'medications']

    def create(self, validated_data):
        request = self.context['request']
        doctor_user = request.user
        case_id = validated_data.pop('case_id')

        # --- Validate diagnosis case ---
        try:
            diagnosis = DiagnosisCase.objects.get(id=case_id)
        except DiagnosisCase.DoesNotExist:
            raise serializers.ValidationError("Diagnosis case not found.")

        # --- Validate doctor assignment ---
        patient = diagnosis.patient
        try:
            doctor_profile = doctor_user.doctor_profile
        except AttributeError:
            raise serializers.ValidationError("Doctor profile not found.")

        if not AssignedDoctor.objects.filter(doctor=doctor_profile, patient=patient).exists():
            raise serializers.ValidationError("You are not assigned to this patient.")

        # --- Create the Visit instance ---
        visit = DiagnosisVisit.objects.create(
            case=diagnosis,
            doctor=doctor_user,
            **validated_data
        )

        for key, file_obj in request.FILES.items():
            if "documents" in key and "file" in key:
                try:
                    index = key.split("[")[1].split("]")[0]
                    doc_type_key = f"documents[ {index}][documentType]"
                    document_type = request.data.get(doc_type_key, "Other")

                except Exception:
                    document_type = "Other"

                try:
                    # Upload file to Cloudinary
                    upload_result = cloudinary.uploader.upload(
                        file_obj,
                        folder="diagnosis_documents/",
                        resource_type="raw"
                    )

                    public_id = upload_result["public_id"]

                    file_url, _ = cloudinary_url(
                        public_id,
                        resource_type="raw",
                        type="upload",
                        sign_url=False
                    )

                    VisitDocument.objects.create(
                        visit=visit,
                        document_type=document_type,
                        file_url=file_url
                    )
                except Exception as e:
                    print("Cloudinary upload failed:", e)


        return visit

# medical/serializers.py

class ScheduledVisitCreateSerializer(serializers.ModelSerializer):
    patient_username = serializers.CharField(write_only=True)
    diagnosis_case_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = ScheduledVisit
        fields = ['patient_username', 'diagnosis_case_id', 'visit_date', 'visit_time', 'notes']

    def create(self, validated_data):
        request = self.context['request']
        doctor_user = request.user

        # Get Doctor profile
        try:
            doctor = doctor_user.doctor_profile
        except AttributeError:
            raise serializers.ValidationError("Doctor profile not found.")

        patient_username = validated_data.pop('patient_username')
        diagnosis_case_id = validated_data.pop('diagnosis_case_id')

        # Validate Patient
        try:
            patient = CustomUser.objects.get(username=patient_username, role=CustomUser.Role.PATIENT)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("Patient not found.")

        # Validate Diagnosis Case
        try:
            diagnosis_case = DiagnosisCase.objects.get(id=diagnosis_case_id, patient=patient)
        except DiagnosisCase.DoesNotExist:
            raise serializers.ValidationError("Diagnosis case not found for this patient.")
        ScheduledVisit.objects.filter(diagnosis_case=diagnosis_case).delete()
        # Create Scheduled Visit
        scheduled_visit = ScheduledVisit.objects.create(
            patient=patient,
            doctor=doctor,
            diagnosis_case=diagnosis_case,
            **validated_data
        )

        # Calculate reminder time (2 hours before visit)
        visit_datetime = datetime.combine(
            scheduled_visit.visit_date, 
            scheduled_visit.visit_time
        )
        visit_datetime = timezone.make_aware(visit_datetime)  # Ensure timezone-aware

        reminder_time = visit_datetime - timedelta(hours=2)

        # Schedule Celery task
        if reminder_time > timezone.now():
            try:  # Only schedule if in future
                print(f"Sending visit reminder to {patient.email} at {reminder_time},of doctor {doctor_user.get_full_name()}")
                # TODO:use send_visit_reminder.apply_async and pass args and eta to schedule the task at a specific time
                send_visit_reminder(
                   patient.email, doctor_user.get_full_name(), reminder_time, scheduled_visit.notes
            )
            except Exception as e:
                raise serializers.ValidationError(str(e))
                

        return scheduled_visit


class ScheduledVisitListSerializer(serializers.ModelSerializer):
    patient_username = serializers.CharField(source='patient.username', read_only=True)
    diagnosis_case_title = serializers.CharField(source='diagnosis_case.title', read_only=True)

    class Meta:
        model = ScheduledVisit
        fields = ['id', 'patient_username', 'diagnosis_case_title', 'visit_date', 'visit_time', 'notes']

# medical/serializers.py

class PatientScheduledVisitListSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(source='doctor.user.get_full_name', read_only=True)
    diagnosis_case_title = serializers.CharField(source='diagnosis_case.title', read_only=True)

    class Meta:
        model = ScheduledVisit
        fields = ['id', 'doctor_name', 'diagnosis_case_title', 'visit_date', 'visit_time', 'notes']
