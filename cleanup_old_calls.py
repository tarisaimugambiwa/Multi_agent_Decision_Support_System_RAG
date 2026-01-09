"""
Cleanup old call records that are stuck in 'initiated' or 'ringing' status
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medical_ai.settings')
django.setup()

from communications.models import Call
from django.utils import timezone
from datetime import timedelta

# Find all calls that are older than 5 minutes and still in initiated/ringing status
time_threshold = timezone.now() - timedelta(minutes=5)

old_calls = Call.objects.filter(
    status__in=['initiated', 'ringing'],
    started_at__lt=time_threshold
)

count = old_calls.count()
print(f"Found {count} old calls stuck in initiated/ringing status")

if count > 0:
    print("\nOld calls:")
    for call in old_calls:
        print(f"- Call ID {call.id}: {call.caller.username} -> {call.receiver.username}, "
              f"Status: {call.status}, Started: {call.started_at}")
    
    # Update them to missed
    old_calls.update(
        status='missed',
        ended_at=timezone.now()
    )
    print(f"\n✓ Updated {count} old calls to 'missed' status")
else:
    print("✓ No cleanup needed")
