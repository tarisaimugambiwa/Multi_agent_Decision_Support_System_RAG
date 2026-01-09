"""
Test incoming calls detection
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medical_ai.settings')
django.setup()

from communications.models import Call
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model

User = get_user_model()

# Get all users
users = User.objects.all()
print("Available users:")
for user in users:
    print(f"  - ID: {user.id}, Username: {user.username}, Role: {user.role}")

print("\n" + "="*60 + "\n")

# Check for calls in the last 60 seconds with status='initiated'
time_threshold = timezone.now() - timedelta(seconds=60)

print(f"Checking for calls started after: {time_threshold}")
print(f"Current time: {timezone.now()}\n")

all_initiated_calls = Call.objects.filter(
    status='initiated'
).select_related('caller', 'receiver').order_by('-started_at')

print(f"All calls with status='initiated':")
if all_initiated_calls.exists():
    for call in all_initiated_calls:
        age_seconds = (timezone.now() - call.started_at).total_seconds()
        print(f"  - Call ID {call.id}: {call.caller.username} → {call.receiver.username}")
        print(f"    Started: {call.started_at} ({age_seconds:.0f} seconds ago)")
        print(f"    Type: {call.call_type}, Status: {call.status}")
        print(f"    Within 60s threshold: {call.started_at >= time_threshold}")
        print()
else:
    print("  No calls with status='initiated'\n")

# Check recent calls (last 5)
print("="*60)
print("\nRecent calls (last 5):")
recent_calls = Call.objects.all().order_by('-started_at')[:5]
for call in recent_calls:
    print(f"  - ID {call.id}: {call.caller.username} → {call.receiver.username}, "
          f"Status: {call.status}, Started: {call.started_at}")
