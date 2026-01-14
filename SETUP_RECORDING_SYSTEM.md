# Quick Setup Script for Call Recording System

## Run these commands in order:

```bash
# 1. Activate virtual environment
.\venv\Scripts\activate

# 2. Install any missing dependencies (if needed)
pip install django

# 3. Create and apply database migrations
python manage.py makemigrations communications
python manage.py migrate

# 4. Create media directory for recordings
mkdir media\call_recordings

# 5. Run the server
python manage.py runserver
```

## Verify Installation:

1. **Check Migration Status:**
   ```bash
   python manage.py showmigrations communications
   ```
   
   Should show `[X]` next to all migrations including the new recording fields.

2. **Test in Django Shell:**
   ```bash
   python manage.py shell
   ```
   
   ```python
   from communications.models import Call
   from django.contrib.auth import get_user_model
   User = get_user_model()
   
   # Check if recording fields exist
   call = Call.objects.first()
   if call:
       print(f"Has recording fields: {hasattr(call, 'is_recording')}")
       print(f"Recording status: {call.is_recording}")
   ```

3. **Check Media Directory:**
   ```bash
   dir media\call_recordings
   ```
   
   Should exist and be empty (will fill up as calls are recorded).

## Settings.py Check:

Ensure these settings exist in your `settings.py`:

```python
import os

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'
```

## URL Configuration Check:

In your main `urls.py`, ensure media files are served in development:

```python
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ... your patterns ...
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

## Test the System:

1. **Login as Doctor**
2. **Navigate to Messages/Communications**
3. **Click on a Nurse's name**
4. **Click "Voice Call" or "Video Call"**
5. **In another browser/incognito:**
   - Login as the Nurse
   - Should see incoming call notification
   - Click "Answer"
6. **Both should connect and see timer**
7. **Recording auto-starts (check console logs)**
8. **Either party clicks "End Call"**
9. **Check `media/call_recordings/` for recorded file**

## Console Logs to Look For:

**When call connects:**
```
=== Initializing Call ===
✓ Peers connected - bidirectional communication established
Starting call timer - connection established
Auto-starting recording...
=== Starting Call Recording ===
✓ Server notified: Recording started
```

**When call ends:**
```
=== Ending Call ===
Stopping recording before ending call...
=== Stopping Call Recording ===
Recording stopped, saving to server...
Saving recording to server... X chunks
✓ Recording saved to server: call_123_recording.webm
✓ Server notified: Recording stopped, Duration: 45 s
✓ Call ended successfully
```

## Troubleshooting:

### Migration Errors:
```bash
# If migration fails, try:
python manage.py migrate communications --fake-initial
# Then:
python manage.py migrate
```

### Recording Not Starting:
- Check browser console for errors
- Ensure microphone/camera permissions granted
- Verify media directory exists and is writable

### Recording Not Saving:
- Check server logs for errors
- Verify MEDIA_ROOT path is correct
- Check file permissions on media/call_recordings/

### Connection Issues:
- Clear browser cache
- Check STUN server connectivity
- Verify both users are on supported browsers (Chrome, Edge, Firefox)

## Browser Support:

✅ Chrome 60+
✅ Edge 79+
✅ Firefox 55+
✅ Safari 14.1+
❌ Internet Explorer (not supported)

## File Sizes (Approximate):

- **Audio-only call (voice):** ~1 MB per minute
- **Video call (720p):** ~5-10 MB per minute
- **Video call (1080p):** ~10-20 MB per minute

## Database Fields Added:

```sql
-- New fields in communications_call table:
connected_at DATETIME NULL
is_recording BOOLEAN DEFAULT 0
recording_started_at DATETIME NULL
recording_ended_at DATETIME NULL
recording_duration INTEGER NULL
recording_file_path VARCHAR(500) NULL
recording_url VARCHAR(200) NULL
```

## Next Steps (Production):

1. Set up S3 or cloud storage for recordings
2. Implement recording encryption
3. Add recording playback interface
4. Set up WebSocket for real-time signaling (better than polling)
5. Add TURN server for better connectivity
6. Implement recording retention policy
7. Add admin interface for managing recordings
8. Set up monitoring/alerts

---

**System Status:** Ready to Test 🚀
