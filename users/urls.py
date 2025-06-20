from django.urls import path
from .views import PatientProfileRetrieveView, RegisterView, PatientProfileCreateUpdateView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('create/profile/', PatientProfileCreateUpdateView.as_view(), name='patient_profile_update'),
    path('profile/', PatientProfileRetrieveView.as_view(), name='patient_profile'),
]