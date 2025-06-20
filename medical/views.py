from rest_framework import generics, permissions
from .models import DiagnosisCase, DiagnosisVisit
from .serializers import DiagnosisCaseSerializer
# Create your views here.
class PatientDiagnosisListView:
    serializer_class = DiagnosisCaseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return DiagnosisCase.objects.filter(patient=self.request.user).order_by('-created_at')
    

class DiagnosisCaseCreateView(generics.ListAPIView):
    queryset = DiagnosisCase.objects.all()
    serializer_class = DiagnosisCaseSerializer
    permission_classes = [permissions.IsAuthenticated]

class DiagnosisVisitCreateView(generics.ListAPIView):
    queryset = DiagnosisVisit.objects.all()
    serializer_class = DiagnosisCaseSerializer
    permission_classes = [permissions.IsAuthenticated]
   
class DiagnosisVisitUpdateView(generics.RetrieveUpdateAPIView):
    queryset = DiagnosisVisit.objects.all()
    serializer_class = DiagnosisCaseSerializer
    permission_classes = [permissions.IsAuthenticated]
