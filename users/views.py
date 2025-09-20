from rest_framework import generics,status
from rest_framework.permissions import AllowAny, IsAuthenticated

from medical.models import AssignedDoctor
from .models import CustomUser, Doctor, PatientProfile
from .serializers import  DoctorCompleteProfileSerializer, DoctorListSerializer, DoctorProfileSerializer, DoctorRegistrationSerializer,  HospitalCompleteProfileSerializer, HospitalProfileSerializer, HospitalRecentPatientAddSerializer, HospitalRecentPatientListSerializer, HospitalRegistrationSerializer, PatientCompleteProfileSerializer, PatientPublicProfileSerializer, PatientRegistrationSerializer,  PatientProfileSerializer
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework import serializers
from rest_framework.views import APIView
class UserMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "id": request.user.id,
            "username": request.user.username,
            "email": request.user.email,
            "role": request.user.role,
        })
class PatientRegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        serializer = PatientRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)  # Log in console
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DoctorRegisterView(generics.CreateAPIView):
    serializer_class = DoctorRegistrationSerializer
    permission_classes=[AllowAny]

class HospitalRegisterView(generics.CreateAPIView):
    serializer_class = HospitalRegistrationSerializer
    permission_classes=[AllowAny]



class PatientProfileCreateUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = PatientProfileSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Try to get existing profile (update)
            profile = request.user.patient_profile
            serializer = self.get_serializer(profile, data=request.data, partial=True)
        except PatientProfile.DoesNotExist:
            # No profile exists (create)
            serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PatientProfileRetrieveView(generics.RetrieveUpdateAPIView):
    serializer_class = PatientProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        try:
            return self.request.user.patient_profile
        except PatientProfile.DoesNotExist:
            return serializers.ValidationError({"detail": "Profile not created yet."})
class PatientCompleteProfileView(generics.RetrieveAPIView):
    serializer_class = PatientCompleteProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
class PatientCompleteProfileUpdateView(generics.UpdateAPIView):
    serializer_class = PatientCompleteProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
class DoctorProfileCreateView(generics.CreateAPIView):
    serializer_class = DoctorProfileSerializer
    permission_classes=[IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class HospitalProfileCreateView(generics.CreateAPIView):
    serializer_class = HospitalProfileSerializer
    permission_classes=[IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class DoctorProfileView(generics.RetrieveAPIView):
    serializer_class = DoctorCompleteProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
    
class HospitalProfileView(generics.RetrieveAPIView):
    serializer_class = HospitalCompleteProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
   


class AddRecentPatientView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = HospitalRecentPatientAddSerializer

    def post(self, request):
        user = request.user
        if user.role != CustomUser.Role.HOSPITAL:
            return Response({"detail": "Only hospitals can add recent patients"}, status=403)

        try:
            hospital = user.hospital_profile
        except AttributeError:
            return Response({"detail": "Hospital profile not found."}, status=400)

        serializer = self.get_serializer(data=request.data, context={"hospital": hospital})
        serializer.is_valid(raise_exception=True)
        patient = serializer.save()

        return Response({
            "detail": f"Patient '{patient.first_name}' added to recent patients."
        }, status=201)
    
class RecentPatientsView(generics.ListAPIView):
    serializer_class = HospitalRecentPatientListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role != CustomUser.Role.HOSPITAL:
            return []

        try:
            hospital = user.hospital_profile
            return hospital.recents_patients.all()
        except AttributeError:
            return CustomUser.objects.none()
        
class HospitalViewPatientProfileView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PatientPublicProfileSerializer
    lookup_field = "username"
    queryset = CustomUser.objects.filter(role=CustomUser.Role.PATIENT)

    def get_object(self):
        user = self.request.user

        if user.role != CustomUser.Role.HOSPITAL:
            raise PermissionDenied("Only hospitals can access patient profiles.")

        try:
            hospital = user.hospital_profile
        except AttributeError:
            raise PermissionDenied("Hospital profile not found.")

        patient_username = self.kwargs.get("username")
        try:
            patient = CustomUser.objects.get(username=patient_username, role=CustomUser.Role.PATIENT)
        except CustomUser.DoesNotExist:
            raise NotFound("Patient not found.")

        # if patient not in hospital.recents_patients.all():
        #     raise PermissionDenied("This patient is not in your recent list.")

        return patient
    
class DoctorAssignedPatientProfileView(generics.RetrieveAPIView):
    serializer_class = PatientPublicProfileSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "username"
    def get_object(self):
        doctor = self.request.user

        if doctor.role != CustomUser.Role.DOCTOR:
            raise PermissionDenied("Only doctors can view patient profiles.")

        try:
            doctor_profile = doctor.doctor_profile
        except AttributeError:
            raise PermissionDenied("Doctor profile not found.")

        username = self.kwargs.get("username")
        try:
            patient = CustomUser.objects.get(username=username, role=CustomUser.Role.PATIENT)
        except CustomUser.DoesNotExist:
            raise NotFound("Patient not found.")

        # Ensure the doctor is assigned to this patient
        if not AssignedDoctor.objects.filter(doctor=doctor_profile, patient=patient).exists():
            raise PermissionDenied("You are not assigned to this patient.")

        return patient


class AddDoctorToHospitalView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        if user.role != CustomUser.Role.HOSPITAL:
            raise PermissionDenied("Only hospitals can add doctors.")

        try:
            hospital = user.hospital_profile
        except AttributeError:
            raise PermissionDenied("Hospital profile not found.")

        doctor_username = request.data.get('username')
        if not doctor_username:
            return Response({"error": "Doctor username is required."}, status=400)

        try:
            doctor_user = CustomUser.objects.get(username=doctor_username, role=CustomUser.Role.DOCTOR)
        except CustomUser.DoesNotExist:
            raise NotFound("Doctor user not found.")

        try:
            doctor_profile = doctor_user.doctor_profile
        except Doctor.DoesNotExist:
            raise NotFound("Doctor profile not found.")

        # Link doctor to hospital
        doctor_profile.hospital = hospital
        doctor_profile.save()
        print(doctor_profile)
        doctor_data = {
        'id': doctor_user.id,
        'username': doctor_user.username,
        'specialization': doctor_profile.specialization,
        'license_number': doctor_profile.license_number
        }
        return Response({"message": f"Doctor '{doctor_username}' added to hospital '{hospital.name}'.",'doctor':doctor_data}, status=200)

class HospitalDoctorProfileView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DoctorCompleteProfileSerializer
    lookup_field = "username"
    queryset = CustomUser.objects.filter(role=CustomUser.Role.DOCTOR)

    def get_object(self):
        user = self.request.user

        if user.role != CustomUser.Role.HOSPITAL:
            raise PermissionDenied("Only hospitals can access doctor profiles.")
        doctor_username = self.kwargs.get("username")
        try:
            patient = CustomUser.objects.get(username=doctor_username, role=CustomUser.Role.DOCTOR)
        except CustomUser.DoesNotExist:
            raise NotFound("Doctor not found.")

        return patient
class HospitalDoctorListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DoctorListSerializer

    def get_queryset(self):
        user = self.request.user

        if user.role != CustomUser.Role.HOSPITAL:
            raise PermissionDenied("Only hospitals can view their doctor list.")

        try:
            hospital = user.hospital_profile
        except AttributeError:
            raise PermissionDenied("Hospital profile not found.")

        return Doctor.objects.filter(hospital=hospital)
    
