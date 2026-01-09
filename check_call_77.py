"""
Check call ID 77 details
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medical_ai.settings')
django.setup()

from communications.models import Call

try:
    call = Call.objects.get(id=77)
    print(f"✓ Call ID 77 exists")
    print(f"  Caller: {call.caller.username}")
    print(f"  Receiver: {call.receiver.username}")
    print(f"  Status: {call.status}")
    print(f"  Call Type: {call.call_type}")
    print(f"  Started: {call.started_at}")
    print(f"  Ended: {call.ended_at}")
except Call.DoesNotExist:
    print("✗ Call ID 77 does not exist in the database")
    
    # Show recent calls
    recent_calls = Call.objects.all().order_by('-started_at')[:5]
    print(f"\nRecent calls:")
    for call in recent_calls:
        print(f"  ID {call.id}: {call.caller.username} -> {call.receiver.username}, "
              f"Status: {call.status}, Started: {call.started_at}")
