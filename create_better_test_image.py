"""
Create a better test image for case #46 - with visible content
"""
import os
import django
import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medical_ai.settings')
django.setup()

from diagnoses.models import Case

# Create a more visible test image with text
def create_better_test_image():
    """Create a test image with visible content"""
    # Create larger image (400x400)
    img = Image.new('RGB', (400, 400), color='white')
    draw = ImageDraw.Draw(img)
    
    # Draw colored rectangles to represent different areas (simulating a wound/symptom image)
    draw.rectangle([50, 50, 150, 150], fill='lightblue', outline='blue', width=2)
    draw.rectangle([200, 50, 300, 150], fill='lightgreen', outline='green', width=2)
    draw.rectangle([50, 200, 150, 300], fill='lightyellow', outline='orange', width=2)
    draw.rectangle([200, 200, 300, 300], fill='lightcoral', outline='red', width=2)
    
    # Draw some text
    try:
        # Try to use default font
        draw.text((50, 320), "Test Medical Image - Case #46", fill='black')
    except:
        pass
    
    img_bytes = BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return img_bytes

# Create image and convert to base64
img_file = create_better_test_image()
base64_image = base64.b64encode(img_file.read()).decode('utf-8')

print(f"Created improved base64 image (length: {len(base64_image)})")
print(f"First 50 chars: {base64_image[:50]}")

# Update case #46 with improved image data
case = Case.objects.get(id=46)
case.symptom_image = base64_image
case.symptom_image_filename = 'snake_bite_documentation.jpg'
case.save()

print(f"\n✅ Case #{case.id} updated with better test image!")
print(f"   - Image stored: {len(case.symptom_image)} chars")
print(f"   - Filename: {case.symptom_image_filename}")
print(f"\n🔄 Refresh your browser at: http://127.0.0.1:8000/diagnoses/{case.id}/")
print(f"   You should now see a colorful test image with rectangles")
