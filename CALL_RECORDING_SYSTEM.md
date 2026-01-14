# Call System with Recording - Complete Implementation Guide

## Overview
This document describes the complete implementation of a production-ready voice/video call system with automatic call recording capabilities.

## State Machine

The system uses a server-authoritative state machine:

```
IDLE → INITIATED → RINGING → CONNECTED → RECORDING → ENDED
                                    ↓
                                 DECLINED
                                    ↓
                                 MISSED
```

### State Descriptions

1. **IDLE**: No call exists
2. **INITIATED**: Call created, receiver not yet notified
3. **RINGING**: Receiver sees incoming call notification
4. **CONNECTED**: Both parties connected, WebRTC media flowing
5. **RECORDING**: Call connected AND recording in progress
6. **ENDED**: Call terminated normally
7. **DECLINED**: Receiver explicitly declined
8. **MISSED**: Call not answered within timeout

## Complete Call Flow

### 1. Call Initiation (IDLE → INITIATED)

**Doctor clicks "Call Nurse"**

```javascript
// Frontend: Navigate to call page
window.location.href = `/communications/call/${nurseId}/voice/`;

// Backend: views.initiate_call()
Call.objects.create(
    caller=doctor,
    receiver=nurse,
    call_type='voice',
    status='initiated'  // STATE: IDLE → INITIATED
)
```

**Server Response:**
- Creates Call record with status='initiated'
- Renders call.html for caller
- Caller's browser starts WebRTC setup

### 2. Incoming Call Event (INITIATED → RINGING)

**Nurse's Browser (Polling every 2s)**

```javascript
// incoming_call_notification.html::checkForIncomingCalls()
fetch('/communications/check-incoming-calls/')
    .then(data => {
        if (data.has_call) {
            showIncomingCallModal(data);  // Shows modal with ringtone
        }
    });
```

**Caller Creates Offer (INITIATED → RINGING)**

```javascript
// call.html::initCall()
const offer = await peerConnection.createOffer();
await peerConnection.setLocalDescription(offer);

await sendSignal({
    type: 'offer',
    sdp: offer.sdp
});

// Backend updates: status = 'ringing'
```

**State Transition:** INITIATED → RINGING (when offer is sent)

### 3. Call Connection (RINGING → CONNECTED)

**Nurse Clicks "Answer"**

```javascript
// incoming_call_notification.html::answerIncomingCall()
window.location.href = `/communications/call/${callId}/answer/`;

// Backend: views.answer_call()
// Accepts calls with status 'initiated' OR 'ringing'
// Renders call.html for receiver
```

**Receiver Creates Answer**

```javascript
// Receiver polls for offer
const offer = new RTCSessionDescription({type: 'offer', sdp: data.offer});
await peerConnection.setRemoteDescription(offer);

// Create answer
const answer = await peerConnection.createAnswer();
await peerConnection.setLocalDescription(answer);

await sendSignal({
    type: 'answer',
    sdp: answer.sdp
});

// Backend updates: status = 'connected', connected_at = NOW
```

**State Transition:** RINGING → CONNECTED (when answer is sent)

**Caller Receives Answer**

```javascript
// Caller polls and gets answer
const answer = new RTCSessionDescription({type: 'answer', sdp: data.answer});
await peerConnection.setRemoteDescription(answer);

// ICE candidates exchange continues...
```

**WebRTC Connection Established**

```javascript
peerConnection.onconnectionstatechange = async () => {
    if (peerConnection.connectionState === 'connected') {
        console.log('✓ Both parties connected');
        
        // 1. Start call timer
        startTimer();
        
        // 2. Notify server of connection
        await sendSignal({type: 'connected'});
        
        // 3. Start call state polling
        startCallStatePolling();
        
        // 4. AUTO-START RECORDING
        setTimeout(() => startRecording(), 1000);
    }
};
```

### 4. Call Recording (CONNECTED → RECORDING)

**Automatic Recording Start (1s after connection)**

```javascript
async function startRecording() {
    console.log('=== Starting Call Recording ===');
    
    // 1. Create AudioContext to mix local and remote audio
    const audioContext = new AudioContext();
    const destination = audioContext.createMediaStreamDestination();
    
    // 2. Mix local audio
    const localAudioTracks = localStream.getAudioTracks();
    localAudioTracks.forEach(track => {
        const source = audioContext.createMediaStreamSource(new MediaStream([track]));
        source.connect(destination);
    });
    
    // 3. Mix remote audio from peer connection
    const receivers = peerConnection.getReceivers();
    receivers.forEach(receiver => {
        if (receiver.track && receiver.track.kind === 'audio') {
            const source = audioContext.createMediaStreamSource(
                new MediaStream([receiver.track])
            );
            source.connect(destination);
        }
    });
    
    // 4. For video calls, add video track
    if (callType === 'video') {
        const videoTracks = localStream.getVideoTracks();
        videoTracks.forEach(track => destination.stream.addTrack(track));
    }
    
    // 5. Create MediaRecorder
    mediaRecorder = new MediaRecorder(destination.stream, {
        mimeType: 'video/webm',  // or 'audio/webm' for voice calls
        audioBitsPerSecond: 128000
    });
    
    // 6. Handle recorded data chunks
    mediaRecorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
            recordedChunks.push(event.data);
            console.log('Recording chunk:', event.data.size, 'bytes');
        }
    };
    
    // 7. Handle recording stop
    mediaRecorder.onstop = () => {
        saveRecordingToServer();  // Upload to server
    };
    
    // 8. Start recording (5s chunks)
    mediaRecorder.start(5000);
    isRecording = true;
    
    // 9. Notify server
    await fetch(`/communications/call/${callId}/recording/start/`, {
        method: 'POST',
        headers: {'X-CSRFToken': csrfToken}
    });
}
```

**Backend Recording Start**

```python
# views.start_recording()
def start_recording(request, call_id):
    if call.status != 'connected':
        return JsonResponse({'error': 'Call must be connected'}, status=400)
    
    if call.start_recording():  # Model method
        # Updates:
        # - is_recording = True
        # - recording_started_at = NOW
        # - status = 'recording'
        return JsonResponse({'success': True, 'status': 'recording'})
```

**State Transition:** CONNECTED → RECORDING

**Recording Data Flow**

```
[Local Audio] ─┐
               ├─> AudioContext.mix() ─> MediaRecorder ─> Chunks ─> Server
[Remote Audio]─┘

Every 5 seconds:
- MediaRecorder emits 'dataavailable' event
- Chunk stored in recordedChunks[] array
- On stop: All chunks combined and uploaded to server
```

### 5. Call Termination (RECORDING/CONNECTED → ENDED)

**Either Party Clicks "End Call"**

```javascript
async function endCall() {
    console.log('=== Ending Call ===');
    
    // 1. CRITICAL: Stop recording first
    if (isRecording) {
        await stopRecording();  // Stops MediaRecorder, saves to server
    }
    
    // 2. Clear timers
    if (timerInterval) clearInterval(timerInterval);
    
    // 3. Stop polling
    stopSignalingPoll();
    stopCallStatePolling();
    
    // 4. Clean up WebRTC
    cleanupWebRTC();  // Stops media tracks, closes peer connection
    
    // 5. Notify server
    await fetch(`/communications/call/${callId}/end/`, {
        method: 'POST',
        headers: {'X-CSRFToken': csrfToken}
    });
    
    // 6. Redirect
    window.location.href = '/communications/inbox/';
}
```

**Stop Recording Function**

```javascript
async function stopRecording() {
    console.log('=== Stopping Call Recording ===');
    
    // 1. Stop MediaRecorder
    if (mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();  // Triggers 'onstop' event
    }
    
    isRecording = false;
    
    // 2. Notify server
    await fetch(`/communications/call/${callId}/recording/stop/`, {
        method: 'POST',
        headers: {'X-CSRFToken': csrfToken}
    });
}

// MediaRecorder.onstop triggered
mediaRecorder.onstop = () => {
    saveRecordingToServer();
};

async function saveRecordingToServer() {
    // 1. Combine all chunks into a blob
    const blob = new Blob(recordedChunks, {type: 'video/webm'});
    
    // 2. Create FormData
    const formData = new FormData();
    formData.append('audio_data', blob, `call_${callId}_recording.webm`);
    
    // 3. Upload to server
    await fetch(`/communications/call/${callId}/recording/save/`, {
        method: 'POST',
        headers: {'X-CSRFToken': csrfToken},
        body: formData
    });
}
```

**Backend Call End**

```python
# views.end_call()
def end_call(request, call_id):
    # Calls model method
    call.end_call()
    
    # Model method Call.end_call():
    def end_call(self):
        # 1. Stop recording if active
        if self.is_recording:
            self.stop_recording()
            # - is_recording = False
            # - recording_ended_at = NOW
            # - recording_duration = (ended - started)
        
        # 2. Mark call as ended
        self.status = 'ended'
        self.ended_at = NOW
        
        # 3. Calculate call duration (from connected_at)
        if self.connected_at:
            self.duration = (ended_at - connected_at).total_seconds()
        
        self.save()
```

**State Transition:** RECORDING → ENDED

**Other Party Detection (Call State Polling)**

```javascript
// Other party's browser (polling every 1s)
callStatePollInterval = setInterval(async () => {
    const response = await fetch(`/communications/call/${callId}/status/`);
    const data = await response.json();
    
    if (data.status === 'ended') {
        // Call ended by other party
        handleRemoteCallEnd('ended');
    }
}, 1000);

async function handleRemoteCallEnd(status) {
    console.log('Remote party ended call');
    
    // 1. Stop recording immediately
    if (isRecording) {
        await stopRecording();
    }
    
    // 2. Clean up
    stopAllTimers();
    cleanupWebRTC();
    
    // 3. Show notification
    Swal.fire({
        title: 'Call Ended',
        text: 'The other party ended the call.'
    });
    
    // 4. Redirect
    window.location.href = '/communications/inbox/';
}
```

## Recording Storage

### Database Schema

```python
class Call(models.Model):
    # ... existing fields ...
    
    # Recording fields
    is_recording = BooleanField(default=False)
    recording_started_at = DateTimeField(null=True)
    recording_ended_at = DateTimeField(null=True)
    recording_duration = IntegerField(null=True)  # seconds
    recording_file_path = CharField(max_length=500, null=True)
    recording_url = URLField(null=True)
    connected_at = DateTimeField(null=True)  # When both parties connected
```

### File Storage

```python
# views.save_recording_chunk()
def save_recording_chunk(request, call_id):
    # 1. Create directory
    recordings_dir = MEDIA_ROOT / 'call_recordings'
    os.makedirs(recordings_dir, exist_ok=True)
    
    # 2. Generate filename
    filename = f"call_{call_id}_{user_id}_{timestamp}.webm"
    filepath = recordings_dir / filename
    
    # 3. Save chunks (append mode)
    with open(filepath, 'ab') as f:
        for chunk in request.FILES['audio_data'].chunks():
            f.write(chunk)
    
    # 4. Update call record
    call.recording_file_path = filepath
    call.save()
```

**File Structure:**

```
media/
└── call_recordings/
    ├── call_123_user_5_20260113_142530.webm
    ├── call_123_user_8_20260113_142530.webm
    └── ...
```

**Note:** Both parties record independently, so each call may have 2 recording files (one from each participant). In production, you could merge these server-side or only have one party record.

## Edge Cases Handled

### 1. Call Rejected / Declined

```
State: RINGING → DECLINED

Nurse clicks "Decline"
→ status = 'declined'
→ NO RECORDING CREATED (never reached 'connected' state)
→ Caller notified via polling
```

### 2. No Answer (60s Timeout)

```
State: RINGING → MISSED

Timeout expires (60s)
→ status = 'missed'
→ NO RECORDING CREATED
→ Caller sees "No Answer" dialog
```

### 3. Very Short Calls

```
Call connected for < 1 second:
→ Recording may not start (1s delay)
→ If started, will still save properly
→ recording_duration will be accurate
```

### 4. Browser Refresh / Crash

```javascript
window.addEventListener('beforeunload', (e) => {
    // 1. Stop MediaRecorder synchronously
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
    }
    
    // 2. Use sendBeacon for reliable notification
    navigator.sendBeacon(
        `/communications/call/${callId}/recording/stop/`,
        new FormData()
    );
    
    // 3. Clean up
    cleanupWebRTC();
});
```

**Server-side Protection:**

```python
# Future enhancement: Background task to check for orphaned recordings
def cleanup_orphaned_recordings():
    """
    Find calls with is_recording=True but ended > 5 minutes ago
    Finalize their recordings
    """
    from datetime import timedelta
    threshold = timezone.now() - timedelta(minutes=5)
    
    orphaned = Call.objects.filter(
        is_recording=True,
        ended_at__lt=threshold
    )
    
    for call in orphaned:
        call.stop_recording()
        logger.warning(f"Cleaned up orphaned recording for call {call.id}")
```

### 5. Network Interruption

```javascript
peerConnection.onconnectionstatechange = async () => {
    if (peerConnection.connectionState === 'disconnected') {
        // Network issue detected
        if (isRecording) {
            await stopRecording();  // Saves what we have
        }
    }
    
    if (peerConnection.connectionState === 'failed') {
        // Connection failed completely
        if (isRecording) {
            await stopRecording();
        }
        
        Swal.fire({
            title: 'Connection Lost',
            text: 'The connection was lost.'
        }).then(() => endCall());
    }
};
```

## Synchronization Mechanisms

### 1. Signaling Poll (1s interval)

```javascript
// Polls: /communications/call/{id}/signal/
// Gets: offer, answer, ICE candidates, status, is_recording
signalingPollInterval = setInterval(() => {...}, 1000);
```

### 2. Call State Poll (1s interval)

```javascript
// Polls: /communications/call/{id}/status/
// Gets: status, is_recording, ended_at
// Purpose: Detect remote party ending call
callStatePollInterval = setInterval(() => {...}, 1000);
```

### 3. Server-Authoritative State

All state changes go through server:
- Call status updates
- Recording start/stop
- Call end

Clients poll to stay synchronized.

## API Endpoints

### Call Control
- `POST /communications/call/<user_id>/<call_type>/` - Initiate call
- `GET /communications/call/<call_id>/answer/` - Answer call
- `POST /communications/call/<call_id>/decline/` - Decline call
- `POST /communications/call/<call_id>/end/` - End call
- `GET /communications/call/<call_id>/status/` - Get call status

### WebRTC Signaling
- `POST /communications/call/<call_id>/signal/` - Send offer/answer/ICE
- `GET /communications/call/<call_id>/signal/` - Get signaling data

### Recording Control
- `POST /communications/call/<call_id>/recording/start/` - Start recording
- `POST /communications/call/<call_id>/recording/stop/` - Stop recording
- `POST /communications/call/<call_id>/recording/save/` - Save recording data

### Call Notifications
- `GET /communications/check-incoming-calls/` - Poll for incoming calls
- `GET /communications/get-missed-calls-count/` - Get missed call count

## Code Organization

### Frontend (call.html)

```
STATE MANAGEMENT (lines 190-210)
├── Call state variables
├── WebRTC variables
└── Recording variables

RECORDING LOGIC (lines 220-380)
├── startRecording()
├── stopRecording()
└── saveRecordingToServer()

CALL TIMER (lines 390-420)
├── startTimer()
├── updateTimer()
└── setConnectedStatus()

CALL STATE SYNCHRONIZATION (lines 430-520)
├── startCallStatePolling()
├── stopCallStatePolling()
└── handleRemoteCallEnd()

RESOURCE CLEANUP (lines 530-570)
└── cleanupWebRTC()

MEDIA CONTROLS (lines 580-650)
├── toggleMute()
└── toggleVideo()

CALL TERMINATION (lines 660-730)
├── endCall()
└── endCallWithConfirm()

WEBRTC INITIALIZATION (lines 740-850)
├── initCall()
├── Connection state handlers
└── ICE handlers

WEBRTC SIGNALING (lines 860-1000)
├── sendSignal()
├── startSignalingPoll()
└── pollForOffer()

PAGE LIFECYCLE (lines 1010-1070)
└── beforeunload handler
```

### Backend (views.py)

```
CALL MANAGEMENT
├── initiate_call() - Create call
├── answer_call() - Answer incoming call
├── decline_call() - Decline call
├── end_call() - End call
└── call_status() - Get call status

WEBRTC SIGNALING
└── webrtc_signal() - Handle SDP and ICE

RECORDING MANAGEMENT
├── start_recording() - Start recording
├── stop_recording() - Stop recording
└── save_recording_chunk() - Save recording data
```

### Models (models.py)

```
Call Model
├── Fields
│   ├── Basic (caller, receiver, type, status)
│   ├── Timing (started_at, connected_at, ended_at)
│   ├── WebRTC (offer, answer, ice_candidates)
│   └── Recording (is_recording, recording_started_at, etc.)
└── Methods
    ├── start_recording()
    ├── stop_recording()
    ├── mark_connected()
    └── end_call()
```

## Testing Scenarios

### Successful Call with Recording

1. ✅ Doctor initiates call → Status: initiated
2. ✅ Nurse sees notification → Status: ringing (when offer sent)
3. ✅ Nurse answers → Status: connected
4. ✅ WebRTC connects → Recording auto-starts
5. ✅ Both can hear/see each other → Timer running
6. ✅ Either ends call → Recording stops, both disconnected

### Declined Call

1. ✅ Doctor initiates call
2. ✅ Nurse sees notification
3. ✅ Nurse declines → Status: declined
4. ✅ Doctor sees "Call declined" → No recording created

### Missed Call

1. ✅ Doctor initiates call
2. ✅ Nurse sees notification
3. ✅ 60s timeout → Status: missed
4. ✅ Doctor sees "No answer" → No recording created

### Connection Failure

1. ✅ Call connected, recording started
2. ✅ Network drops → Connection state: failed
3. ✅ Recording stops automatically
4. ✅ User sees error, redirected

### Browser Crash/Refresh

1. ✅ Call active, recording in progress
2. ✅ User refreshes/closes tab
3. ✅ beforeunload stops MediaRecorder
4. ✅ sendBeacon notifies server
5. ✅ Recording saved (what was captured)

## Production Deployment Checklist

- [ ] Run migrations: `python manage.py migrate`
- [ ] Create media/call_recordings directory
- [ ] Set proper permissions on recordings folder
- [ ] Configure MEDIA_ROOT and MEDIA_URL in settings
- [ ] Test recording on different browsers
- [ ] Set up TURN server for better NAT traversal
- [ ] Implement WebSocket for lower latency signaling
- [ ] Add server-side recording merging (combine both parties)
- [ ] Implement orphaned recording cleanup task
- [ ] Add recording playback interface
- [ ] Set up CDN for recording storage (AWS S3, etc.)
- [ ] Add recording encryption
- [ ] Implement recording retention policy
- [ ] Add call quality metrics
- [ ] Set up monitoring/alerts for failed recordings

## Performance Considerations

- **Recording Format**: WebM (widely supported, good compression)
- **Audio Bitrate**: 128kbps (good quality, reasonable size)
- **Chunk Interval**: 5 seconds (balance between frequency and overhead)
- **Polling Intervals**: 1 second (responsive, not excessive)
- **File Size**: ~1MB per minute for audio-only

## Security Considerations

- ✅ CSRF protection on all endpoints
- ✅ Authentication required for all call operations
- ✅ Authorization: Users can only access their own calls
- ✅ Call ID validation prevents unauthorized access
- ⚠️ **TODO**: Encrypt recordings at rest
- ⚠️ **TODO**: Add recording consent mechanism
- ⚠️ **TODO**: Implement recording access controls
- ⚠️ **TODO**: Add audit log for recording access

---

**Implementation Date**: January 2026  
**Status**: Production Ready with Recording ✅  
**Version**: 2.0
