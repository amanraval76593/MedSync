from django.urls import path
from .views import PatientDiagnosisListView, DiagnosisVisitUpdateView, DiagnosisVisitCreateView, DiagnosisCaseCreateView

urlpatterns = [
    path('diagnosis/', PatientDiagnosisListView.as_view(), name='patient-diagnosis-list'),
    path('diagnosis/create/', DiagnosisCaseCreateView.as_view(), name='diagnosis-case-create'),
    path('diagnosis/visit/create/', DiagnosisVisitCreateView.as_view(), name='diagnosis-visit-create'),
    path('diagnosis/visit/<int:pk>/update/', DiagnosisVisitUpdateView.as_view(), name='diagnosis-visit-update'),
]


