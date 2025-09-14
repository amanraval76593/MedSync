from django.urls import path

from .views import AddDoctorToHospitalView, AddRecentPatientView, DoctorAssignedPatientProfileView, DoctorProfileCreateView, DoctorProfileView, HospitalDoctorListView, HospitalDoctorProfileView, HospitalProfileCreateView, HospitalProfileView, HospitalViewPatientProfileView, PatientCompleteProfileUpdateView, PatientCompleteProfileView, PatientProfileRetrieveView, PatientProfileCreateUpdateView,PatientRegisterView,DoctorRegisterView,HospitalRegisterView, RecentPatientsView, UserMeView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('register/patient/', PatientRegisterView.as_view(), name='register_patient'),
    path('register/doctor/', DoctorRegisterView.as_view(), name='register_doctor'),
    path('register/hospital/', HospitalRegisterView.as_view(), name='register_hospital'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('patient/create/profile/', PatientProfileCreateUpdateView.as_view(), name='patient_profile_update'),
    path('patient/profile/', PatientCompleteProfileView.as_view(), name='patient_profile'),
    path('patient/profile/update/', PatientCompleteProfileUpdateView.as_view(), name='patient_profile'),
    path('doctor/profile/', DoctorProfileView.as_view(), name='doctor-profile'),
    path('hospital/profile/', HospitalProfileView.as_view(), name='hospital-profile'),
    path('doctor/create/profile/', DoctorProfileCreateView.as_view(), name='doctor_profile_create'),
    path('hospital/create/profile/', HospitalProfileCreateView.as_view(), name='hospital_profile_create'),
    path("user/me/", UserMeView.as_view(), name="user-me"),
    path("hospital/add-recent-patient/", AddRecentPatientView.as_view(), name="add-recent-patient"),
    path("hospital/patient-list/", RecentPatientsView.as_view(), name="recent-patients"),
    path("hospital/view-patient/<str:username>/", HospitalViewPatientProfileView.as_view(), name="patient-profile"),
    path("hospital/add-doctor/",AddDoctorToHospitalView.as_view(),name="add-doctor-to-hospital"),
    path("hospital/view-doctor/<str:username>/",HospitalDoctorProfileView.as_view(),name="hospital-doctor-profile"),
    path("hospital/doctor-list/", HospitalDoctorListView.as_view(), name="hospital-doctor-list"),
    path("doctor/assigned-patient/<str:username>/", DoctorAssignedPatientProfileView.as_view(), name="doctor-assigned-patient-profile"),
    path("doctor/view-patient/<str:username>/", DoctorAssignedPatientProfileView.as_view(), name="patient-profile"),
]