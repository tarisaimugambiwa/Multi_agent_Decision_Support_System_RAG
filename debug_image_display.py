"""
Test to verify image is being displayed correctly in template
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medical_ai.settings')
django.setup()

from diagnoses.models import Case
from django.template import Template, Context

# Get case #46
case = Case.objects.get(id=46)

print("=" * 60)
print("DEBUGGING CASE #46 IMAGE DISPLAY")
print("=" * 60)

print(f"\n1. Database Check:")
print(f"   - Has symptom_image: {bool(case.symptom_image)}")
print(f"   - Image length: {len(case.symptom_image) if case.symptom_image else 0} chars")
print(f"   - Filename: {case.symptom_image_filename}")
print(f"   - First 50 chars: {case.symptom_image[:50] if case.symptom_image else 'N/A'}")

# Test the template rendering
template_str = """
{% if case.symptom_image %}
<img src="data:image/jpeg;base64,{{ case.symptom_image }}" alt="test">
CONDITION: TRUE - Image should display
{% else %}
NO IMAGE DATA
CONDITION: FALSE
{% endif %}
"""

template = Template(template_str)
context = Context({'case': case})
rendered = template.render(context)

print(f"\n2. Template Rendering Test:")
print(f"   Result:")
for line in rendered.split('\n'):
    if line.strip():
        print(f"   {line.strip()}")

# Test if image data is corrupted
print(f"\n3. Image Data Validation:")
try:
    import base64
    if case.symptom_image:
        # Try to decode it back
        try:
            decoded = base64.b64decode(case.symptom_image)
            print(f"   - Base64 decode: SUCCESS ({len(decoded)} bytes)")
        except Exception as e:
            print(f"   - Base64 decode: FAILED - {e}")
except Exception as e:
    print(f"   - Error: {e}")

# Check if image field is empty string vs None
print(f"\n4. Field Type Check:")
print(f"   - Type: {type(case.symptom_image)}")
print(f"   - Is None: {case.symptom_image is None}")
print(f"   - Is empty string: {case.symptom_image == ''}")
print(f"   - Bool value: {bool(case.symptom_image)}")

print("\n" + "=" * 60)
print("If condition is TRUE and image data looks valid, then template")
print("should display the image at http://127.0.0.1:8000/diagnoses/46/")
print("=" * 60)
