"""
Script to create demo users for the Medical AI System.
Run this to set up nurse and doctor accounts for testing.
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medical_ai.settings')
django.setup()

from users.models import User

def create_demo_users():
    """Create demo nurse and doctor accounts"""
    
    print("🏥 Creating demo users for Medical AI System...")
    print("-" * 60)
    
    # Create Nurse Account
    nurse_username = 'nurse'
    if User.objects.filter(username=nurse_username).exists():
        print(f"✓ Nurse account '{nurse_username}' already exists")
        nurse = User.objects.get(username=nurse_username)
        # Update to ensure it has the right role
        nurse.role = 'NURSE'
        nurse.save()
    else:
        nurse = User.objects.create_user(
            username=nurse_username,
            password='nurse123',
            email='nurse@hospital.com',
            first_name='Sarah',
            last_name='Johnson',
            role='NURSE'
        )
        print(f"✓ Created nurse account: {nurse_username}")
    
    # Create Doctor Account
    doctor_username = 'doctor'
    if User.objects.filter(username=doctor_username).exists():
        print(f"✓ Doctor account '{doctor_username}' already exists")
        doctor = User.objects.get(username=doctor_username)
        # Update to ensure it has the right role
        doctor.role = 'DOCTOR'
        doctor.save()
    else:
        doctor = User.objects.create_user(
            username=doctor_username,
            password='doctor123',
            email='doctor@hospital.com',
            first_name='James',
            last_name='Wilson',
            role='DOCTOR'
        )
        print(f"✓ Created doctor account: {doctor_username}")
    
    print("-" * 60)
    print("✅ Demo users created successfully!\n")
    print("📋 LOGIN CREDENTIALS:")
    print("-" * 60)
    print("👩‍⚕️ NURSE ACCOUNT:")
    print("   Username: nurse")
    print("   Password: nurse123")
    print("   Role: Nurse")
    print("   Access: Patient Care, Cases, Medical Records\n")
    
    print("👨‍⚕️ DOCTOR ACCOUNT:")
    print("   Username: doctor")
    print("   Password: doctor123")
    print("   Role: Doctor")
    print("   Access: Patients, Medical Records, Knowledge Base\n")
    
    print("-" * 60)
    print("🌐 Login at: http://127.0.0.1:8001/accounts/login/")
    print("-" * 60)

if __name__ == '__main__':
    create_demo_users()
