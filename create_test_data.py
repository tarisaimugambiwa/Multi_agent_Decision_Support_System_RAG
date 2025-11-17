#!/usr/bin/env python
"""Create test data for workflow testing"""
import os
import sys
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medical_ai.settings')
django.setup()

from django.contrib.auth import get_user_model
from patients.models import Patient

User = get_user_model()

# Create or get test patient
patient, created = Patient.objects.get_or_create(
    first_name='Test',
    last_name='Patient',
    defaults={
        'phone_number': '555-1234',
        'gender': 'M',
        'date_of_birth': datetime.now().date() - timedelta(days=365*30)
    }
)

if created:
    print(f'✓ Created patient: {patient.first_name} {patient.last_name}')
else:
    print(f'✓ Using existing patient: {patient.first_name} {patient.last_name}')
print(f'✓ Total patients: {Patient.objects.count()}')
print(f'✓ Nurses available: {User.objects.filter(role="NURSE").count()}')
print(f'✓ Doctors available: {User.objects.filter(role="DOCTOR").count()}')
