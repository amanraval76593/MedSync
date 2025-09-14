from rest_framework import serializers

from medical.models import AssignedDoctor
from .models import CustomUser, Doctor, Hospital
from django.contrib.auth.password_validation import validate_password
from .models import PatientProfile

class PatientRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'password', 'first_name', 'last_name')

    def create(self, validated_data):
        password = validated_data.pop('password')

        user = CustomUser(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role=CustomUser.Role.PATIENT  
        )
        user.set_password(password)
        user.save()
        return user
    
class DoctorRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    specialization = serializers.CharField(write_only=True)
    license_number = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'password', 'first_name', 'last_name', 'specialization', 'license_number')

    def create(self, validated_data):
        password = validated_data.pop('password')
        specialization = validated_data.pop('specialization')
        license_number = validated_data.pop('license_number')
        user = CustomUser(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role=CustomUser.Role.DOCTOR 
        )
        user.set_password(password)
        user.save()

        Doctor.objects.create(
            user=user,
            specialization=specialization,
            license_number=license_number,
            hospital=None
        )
        return user
    
class HospitalRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    name = serializers.CharField(write_only=True)
    address = serializers.CharField(write_only=True)
    phone = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True, required=False)

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'password', 'name', 'address', 'phone')

    def create(self, validated_data):
        password = validated_data.pop('password')
        name = validated_data.pop('name')
        address = validated_data.pop('address')
        phone = validated_data.pop('phone')
        email = validated_data.pop('email', '')

        user = CustomUser(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            role=CustomUser.Role.HOSPITAL,
        )
        user.set_password(password)
        user.save()

        Hospital.objects.create(
            user=user,
            name=name,
            address=address,
            phone=phone,
            email=email
        )
       

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

class PatientCompleteProfileSerializer(serializers.ModelSerializer):
    patient_profile=PatientProfileSerializer()
    class Meta:
        model=CustomUser
        fields=['id', 'username', 'email', 'first_name', 'last_name', 'role', 'patient_profile']
    def update(self, instance, validated_data):
        patient_data=validated_data.pop('patient_profile',{})
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        patient_profile = instance.patient_profile
        for attr,value in patient_data.items():
            setattr(patient_profile, attr, value)
        patient_profile.save()
        return instance

class HospitalProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hospital
        fields = ['name', 'address', 'phone', 'email']
        read_only_fields = ['user']


class DoctorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ['specialization', 'license_number', 'hospital']
        read_only_fields = ['user']



class DoctorCompleteProfileSerializer(serializers.ModelSerializer):
    doctor_profile = DoctorProfileSerializer()

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'doctor_profile', 'role']
        read_only_fields = ['role']

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('doctor_profile', {})
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        doctor_profile = instance.doctor_profile
        for attr, value in profile_data.items():
            setattr(doctor_profile, attr, value)
        doctor_profile.save()

        return instance


class HospitalCompleteProfileSerializer(serializers.ModelSerializer):
    hospital_profile = HospitalProfileSerializer()

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'hospital_profile', 'role']
        read_only_fields = ['role']

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('hospital_profile', {})
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        hospital_profile = instance.hospital_profile
        for attr, value in profile_data.items():
            setattr(hospital_profile, attr, value)
        hospital_profile.save()

        return instance


class HospitalRecentPatientAddSerializer(serializers.Serializer):
    username = serializers.CharField()

    def validate_username(self, value):
        try:
            user = CustomUser.objects.get(username=value)
            if user.role != CustomUser.Role.PATIENT:
                raise serializers.ValidationError("User is not a patient.")
            return value
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("Patient with this username does not exist.")

    def save(self, **kwargs):
        hospital = self.context['hospital']
        username = self.validated_data['username']
        patient = CustomUser.objects.get(username=username)
        #TODO: check if patient is already in recent patients
        hospital.recents_patients.add(patient)
        return patient
    
class HospitalRecentPatientListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username','email', 'first_name', 'last_name', ]
class AssignedDoctorInfoSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')

    class Meta:
        model = Doctor
        fields = ['id', 'username', 'first_name', 'last_name', 'specialization', 'license_number']

class PatientPublicProfileSerializer(serializers.ModelSerializer):
    patient_profile = PatientProfileSerializer()
    assigned_doctors = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser  
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'patient_profile', 'assigned_doctors']

    def get_assigned_doctors(self, obj):
        request = self.context.get("request")
        hospital_user = request.user
        try:
            hospital = hospital_user.hospital_profile
        except:
            return []

        # Get latest assignment by assigned_at timestamp
        latest_assignment = AssignedDoctor.objects.filter(
            hospital=hospital, patient=obj
        ).order_by('-assigned_at').first()

        if latest_assignment:
            return [AssignedDoctorInfoSerializer(latest_assignment.doctor).data]
        return []

class DoctorListSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username")
    email = serializers.EmailField(source="user.email")
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Doctor
        fields = ['id', 'username', 'email', 'full_name', 'specialization', 'license_number']

    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"


