from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth.password_validation import validate_password
from .models import PatientProfile

class RegisterSerializer(serializers.ModelSerializer):
    password=serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],)
    class Meta:
        model=CustomUser
        fields=('id', 'username', 'email', 'password','first_name','last_name', 'role')
    def create(self,validated_data):
        password = validated_data.pop('password')
        
        print("Creating user with password:", password)
        print("Remaining validated_data:", validated_data)
        user=CustomUser(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            # password=password 
            )
        user.role = validated_data.get('role', CustomUser.Role.PATIENT)
        user.set_password(password)
        user.save()
        print(f"Password check after creation: {user.check_password(password)}")
        return user
    
class PatientProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientProfile
        fields = [
            'blood_group',
            'weight',
            'weight_measured_on',
            'height',
            'date_of_birth',
            'existing_conditions',
            'allergies',
        ]
        read_only= ('user', 'created_at', 'updated_at')

