from rest_framework.response import Response
from rest_framework import generics, permissions
from datetime import date
from users.models import CustomUser
from .models import DiagnosisCase, DiagnosisVisit,AssignedDoctor, ScheduledVisit
from rest_framework.exceptions import PermissionDenied, NotFound
from .serializers import AssignDoctorSerializer, AssignedPatientSerializer, CreateDiagnosisCaseSerializer, DiagnosisCaseDetailSerializer, DiagnosisCaseSerializer, DiagnosisCaseSummarySerializer, DiagnosisCaseWithVisitsSerializer, DiagnosisVisitCreateSerializer, DiagnosisVisitSerializer, DoctorDiagnosisVisitCreateSerializer, PatientScheduledVisitListSerializer, ScheduledVisitCreateSerializer, ScheduledVisitListSerializer
# Create your views here.
class PatientDiagnosisListView(generics.ListAPIView):
    serializer_class = DiagnosisCaseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return DiagnosisCase.objects.filter(patient=self.request.user).order_by('-created_at')

class PatientVisitListView(generics.ListAPIView):
    serializer_class = DiagnosisVisitSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return DiagnosisVisit.objects.filter(patient=self.request.user).order_by('-created_at')

class DiagnosisCaseCreateView(generics.ListCreateAPIView):
    queryset = DiagnosisCase.objects.all()
    serializer_class = DiagnosisCaseSerializer
    permission_classes = [permissions.IsAuthenticated]

class DiagnosisVisitCreateView(generics.CreateAPIView):
    queryset = DiagnosisVisit.objects.all()
    serializer_class = DiagnosisVisitCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self,  request, *args, **kwargs):
        print("DEBUG RAW DATA →", request.data)
        return super().create(request, *args, **kwargs)

   
class DiagnosisVisitUpdateView(generics.RetrieveUpdateAPIView):
    queryset = DiagnosisVisit.objects.all()
    serializer_class = DiagnosisCaseSerializer
    permission_classes = [permissions.IsAuthenticated]


class DiagnosisVisitListByCaseView(generics.ListAPIView):
    serializer_class = DiagnosisVisitSerializer
    permission_classes = [ permissions.IsAuthenticated]

    def get_queryset(self):
        case_id = self.request.query_params.get('case_id')
        return DiagnosisVisit.objects.filter(case_id=case_id).order_by('-visit_date')
    

class DiagnosisCaseDetailView(generics.RetrieveAPIView):
    queryset = DiagnosisCase.objects.all()
    serializer_class = DiagnosisCaseDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'


class HospitalViewPatientDiagnosisListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DiagnosisCaseWithVisitsSerializer

    def get_queryset(self):
        user = self.request.user

        if user.role != CustomUser.Role.HOSPITAL:
            raise PermissionDenied("Only hospitals can access diagnosis details.")

        try:
            hospital = user.hospital_profile
        except AttributeError:
            raise PermissionDenied("Hospital profile not found.")

        patient_username = self.kwargs.get("username")
        try:
            patient = CustomUser.objects.get(username=patient_username, role=CustomUser.Role.PATIENT)
        except CustomUser.DoesNotExist:
            raise NotFound("Patient not found.")

        if patient not in hospital.recents_patients.all():
            raise PermissionDenied("Patient is not in your recent patients list.")

        return DiagnosisCase.objects.filter(patient=patient)
    


    

class AssignDoctorToPatientView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AssignDoctorSerializer

    def post(self, request):
        user = request.user
        reassign=request.data.get('reassign')
        if user.role != CustomUser.Role.HOSPITAL:
            return Response({"detail": "Only hospitals can assign doctors."}, status=403)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        hospital = user.hospital_profile
        doctor = serializer.validated_data['doctor']
        patient = serializer.validated_data['patient']

        # Check patient is in hospital's recent list
        if patient not in hospital.recents_patients.all():
            return Response({"detail": "Patient not registered with this hospital."}, status=400)

        if reassign:
            assignment = AssignedDoctor.objects.filter(hospital=hospital, patient=patient).first()
            if assignment:
                assignment.delete()
        assignment, created = AssignedDoctor.objects.get_or_create(
            hospital=hospital,
            doctor=doctor,
            patient=patient
        )

        if not created:
            return Response({"detail": "This doctor is already assigned to this patient."}, status=200)

        return Response({
            "detail": f"Doctor '{doctor.user.username}' assigned to patient '{patient.username}'."
        }, status=201)
    

class DoctorAssignedPatientsView(generics.ListAPIView):
    serializer_class = AssignedPatientSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role != CustomUser.Role.DOCTOR:
            raise PermissionDenied("Only doctors can view assigned patients.")

        try:
            doctor_profile = user.doctor_profile
        except AttributeError:
            raise PermissionDenied("Doctor profile not found.")

        return AssignedDoctor.objects.filter(doctor=doctor_profile)
    
class DoctorPatientDiagnosisListView(generics.ListAPIView):
    serializer_class = DiagnosisCaseSummarySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        doctor = self.request.user

        if doctor.role != CustomUser.Role.DOCTOR:
            raise PermissionDenied("Only doctors can access this endpoint.")

        try:
            doctor_profile = doctor.doctor_profile
        except AttributeError:
            raise PermissionDenied("Doctor profile not found.")

        username = self.kwargs.get("username")
        try:
            patient = CustomUser.objects.get(username=username, role=CustomUser.Role.PATIENT)
        except CustomUser.DoesNotExist:
            raise NotFound("Patient not found.")

        if not AssignedDoctor.objects.filter(doctor=doctor_profile, patient=patient).exists():
            raise PermissionDenied("You are not assigned to this patient.")

        return DiagnosisCase.objects.filter(patient=patient)
    
class DoctorCreateDiagnosisView(generics.CreateAPIView):
    serializer_class = CreateDiagnosisCaseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()

class DoctorCreateVisitView(generics.CreateAPIView):
    serializer_class = DoctorDiagnosisVisitCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()

class ScheduleVisitView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated] 
    serializer_class = ScheduledVisitCreateSerializer
    queryset = ScheduledVisit.objects.all()

class DoctorTodayScheduledVisitsView(generics.ListAPIView):
    serializer_class = ScheduledVisitListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role != CustomUser.Role.DOCTOR:
            raise PermissionDenied("Only doctors can access this view.")
        
        today = date.today()
        return ScheduledVisit.objects.filter(
            doctor__user=user,
            visit_date__date__gte=today
        ).order_by("visit_time")
    

class PatientTodayScheduledVisitsView(generics.ListAPIView):
    serializer_class = PatientScheduledVisitListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role != CustomUser.Role.PATIENT:
            raise PermissionDenied("Only patients can access this view.")
        
        today = date.today()
        return ScheduledVisit.objects.filter(
            patient=user,
            visit_date__date__gte=today
            # visit_date__date=today
        ).order_by("visit_time")