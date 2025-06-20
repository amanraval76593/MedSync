from django.shortcuts import render
from rest_framework import generics,status
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import CustomUser, PatientProfile
from .serializers import RegisterSerializer, PatientProfileSerializer
from rest_framework.response import Response

from rest_framework import serializers

class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

class PatientProfileCreateUpdateView(generics.CreateAPIView):
    serializer_class = PatientProfileSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if hasattr(request.user, 'patient_profile'):
            return Response({"detail": "Profile already exists."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PatientProfileRetrieveView(generics.RetrieveUpdateAPIView):
    serializer_class = PatientProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        try:
            return self.request.user.patient_profile
        except PatientProfile.DoesNotExist:
            return serializers.ValidationError({"detail": "Profile not created yet."})

   