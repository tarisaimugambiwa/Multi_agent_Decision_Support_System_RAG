"""
Quick test to verify patient search is working
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medical_ai.settings')
django.setup()

from patients.models import Patient

# List all patients
patients = Patient.objects.all()
print(f"\n✅ Total patients in database: {patients.count()}")

if patients.exists():
    print("\nSample patients:")
    for patient in patients[:5]:
        print(f"  - ID: {patient.id}, Name: {patient.first_name} {patient.last_name}, Phone: {patient.phone_number}")
    
    # Test search
    test_query = patients.first().first_name[:3]
    print(f"\n🔍 Testing search with query: '{test_query}'")
    
    from django.db.models import Q
    results = Patient.objects.filter(
        Q(first_name__icontains=test_query) |
        Q(last_name__icontains=test_query) |
        Q(phone_number__icontains=test_query)
    )
    
    print(f"✅ Found {results.count()} matching patients:")
    for patient in results[:3]:
        print(f"  - {patient.first_name} {patient.last_name}")
else:
    print("\n⚠️ No patients in database. Create some test patients first.")
    print("Run: python create_test_data.py")
