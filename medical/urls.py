from django.urls import path
from .views import AssignDoctorToPatientView, DiagnosisCaseDetailView, DoctorAssignedPatientsView, DoctorCreateDiagnosisView, DoctorCreateVisitView, DoctorPatientDiagnosisListView, DoctorTodayScheduledVisitsView, HospitalViewPatientDiagnosisListView, PatientDiagnosisListView, DiagnosisVisitUpdateView, DiagnosisVisitCreateView, DiagnosisCaseCreateView,DiagnosisVisitListByCaseView, PatientTodayScheduledVisitsView, ScheduleVisitView

urlpatterns = [
    path('diagnosis/', PatientDiagnosisListView.as_view(), name='patient-diagnosis-list'),
    path('diagnosis/create/', DiagnosisCaseCreateView.as_view(), name='diagnosis-case-create'),
    path('diagnosis/visit/create/', DiagnosisVisitCreateView.as_view(), name='diagnosis-visit-create'),
    path('diagnosis/visit/<int:pk>/update/', DiagnosisVisitUpdateView.as_view(), name='diagnosis-visit-update'),
    path('diagnosis/visits/', DiagnosisVisitListByCaseView.as_view(), name='visit-list-by-case'),
    path('diagnosis_detail/<int:id>/', DiagnosisCaseDetailView.as_view(), name='diagnosis-detail'),
    path("hospital/patient/<str:username>/diagnosis/", HospitalViewPatientDiagnosisListView.as_view(), name="hospital-patient-diagnosis"),
    path("hospital/assign-doctor/", AssignDoctorToPatientView.as_view(), name="assign-doctor-to-patient"),
    path("doctor/assigned-patients/", DoctorAssignedPatientsView.as_view(), name="doctor-assigned-patients"),
    path("doctor/assigned-patient/<str:username>/diagnosis/",DoctorPatientDiagnosisListView.as_view(),name="doctor-patient-diagnosis-list",),
    path("doctor/diagnosis/create/", DoctorCreateDiagnosisView.as_view(), name="doctor-create-diagnosis"),
    path("doctor/diagnosis/visit/create/", DoctorCreateVisitView.as_view(), name="doctor-create-diagnosis-visit"),
    path("doctor/schedule-visit/", ScheduleVisitView.as_view(), name="schedule-visit"),
    path("doctor/scheduled-visits/", DoctorTodayScheduledVisitsView.as_view(), name="doctor-today-visits"),
    path("patient/scheduled-visits/", PatientTodayScheduledVisitsView.as_view(), name="patient-today-visits"),

]


