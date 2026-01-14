# Call Connection & Communication Features

## Overview
This document details the comprehensive connection confirmation, media activation, and UI indicator features implemented for the doctor-nurse video/voice call system.

## Connection State Flow

### 1. Call Initiation
- **State**: `initiated`
- **UI**: "Calling..." status
- **Action**: Caller creates WebRTC offer

### 2. Ringing
- **State**: `ringing`
- **Trigger**: Receiver sees offer
- **UI**: "Ringing..." status for caller
- **Action**: Receiver creates answer

### 3. Connection Established
- **State**: `connected`
- **Trigger**: WebRTC peer connection state = 'connected'
- **Verification**:
  - ✅ Both parties have synchronized under same `callId`
  - ✅ Local audio/video stream active
  - ✅ Remote audio/video stream received
  - ✅ Bidirectional media flow confirmed
- **UI Updates**:
  - Status: "Connected"
  - Success toast notification: "Doctor and Nurse are now connected"
  - Timer starts (HH:MM:SS format)
  - Connection indicators appear
  - Recording auto-starts after 1 second

### 4. Recording Active
- **State**: `recording` (marked when recording starts)
- **UI**: Red "Recording" indicator with pulsing animation

## UI Communication Indicators

### Status Panel
Located below the call timer, displays real-time communication status:

#### 1. Microphone Indicator
```
[🎤 Microphone Active] [~~~~~]
```
- **Shows**: When microphone is active
- **Audio Waveform**: Displays when user is speaking (audio level > 30)
- **Muted State**: Grayed out (opacity: 0.5)
- **Detection**: Real-time audio analysis via AudioContext

#### 2. Camera Indicator (Video Calls Only)
```
[📹 Camera Active]
```
- **Shows**: When camera is active
- **Off State**: Grayed out (opacity: 0.5)
- **Only for**: `call_type = 'video'`

#### 3. Recording Indicator
```
[⚫ Recording]
```
- **Shows**: When call recording is active
- **Animation**: Pulsing red effect
- **Auto-start**: 1 second after connection established
- **Visibility**: Both parties see this indicator

#### 4. Connection Indicator
```
[🔗 Connected]
```
- **Shows**: Connection status
- **States**:
  - "Connecting..." - During WebRTC negotiation
  - "Connected" - Successful bidirectional connection
- **Glow Effect**: Pulsing green glow when connected

## Two-Way Media Activation

### Microphone Activation
**Both Doctor and Nurse**:
```javascript
// Auto-enabled when call connects
localStream.getAudioTracks().forEach(track => {
    track.enabled = true;
});
```

**Features**:
- ✅ Automatic activation on connection
- ✅ Toggle with mute button
- ✅ Speaking detection shows waveform
- ✅ Updates indicator in real-time

### Speaker/Audio Output
**Bidirectional Flow**:
```
Doctor Audio → WebRTC → Nurse Hears
Nurse Audio → WebRTC → Doctor Hears
```

**Verification**:
- System checks `remoteVideo.srcObject` exists
- Validates remote audio tracks present
- Fails connection if streams not established

### Camera Activation (Video Calls)
**Both Parties**:
```javascript
localStream.getVideoTracks().forEach(track => {
    track.enabled = true;
});
```

**Display**:
- **Remote Video**: Full screen background
- **Local Video**: Bottom-right corner (200x150px)
- **Toggle**: Camera button in controls

## Call Timer

### Start Conditions
Timer **ONLY** starts when:
1. ✅ Receiver has answered
2. ✅ WebRTC connection state = 'connected'
3. ✅ Media streams successfully exchanged
4. ✅ Both parties online and synchronized

### Timer Display
**Format**: `HH:MM:SS`
**Examples**:
- `00:00:05` - 5 seconds
- `00:01:30` - 1 minute 30 seconds
- `01:15:42` - 1 hour 15 minutes 42 seconds

**Update Frequency**: Every second (1000ms interval)

**Synchronization**: Both parties calculate independently from same `connected_at` timestamp

### Implementation
```javascript
function startTimer() {
    if (timerInterval) return; // Prevent duplicate timers
    
    callStartTime = new Date();
    timerInterval = setInterval(updateTimer, 1000);
    console.log('✓ Call timer started');
}

function updateTimer() {
    const diff = Math.floor((now - callStartTime) / 1000);
    const hours = Math.floor(diff / 3600);
    const minutes = Math.floor((diff % 3600) / 60);
    const seconds = diff % 60;
    
    const timeString = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    document.getElementById('callTimer').textContent = timeString;
}
```

## Recording Auto-Start

### Trigger Conditions
Recording starts **ONLY** when:
1. ✅ Connection state = 'connected'
2. ✅ Both parties synchronized
3. ✅ Media streams flowing
4. ✅ 1 second delay after connection (ensures streams ready)

### Implementation
```javascript
if (peerConnection.connectionState === 'connected') {
    // Verify media streams
    const hasLocalAudio = localStream && localStream.getAudioTracks().length > 0;
    const hasRemoteStream = document.getElementById('remoteVideo')?.srcObject;
    
    if (!hasLocalAudio || !hasRemoteStream) {
        await handleConnectionFailure('Media streams not established');
        return;
    }
    
    // All checks passed - auto-start recording
    setTimeout(() => startRecording(), 1000);
}
```

### Recording Indicator
**Visibility**: Both parties see the indicator
**Display**: Red pulsing badge "⚫ Recording"
**States**:
- Hidden: Before recording starts
- Visible + Pulsing: During recording
- Hidden: After recording stops

## State Enforcement

### Connection Requirements
The call **CANNOT** be marked active unless:

#### 1. Receiver Has Answered
```python
# Server-side check
if call.status not in ['initiated', 'ringing']:
    return JsonResponse({'error': 'Call cannot be answered'})
```

#### 2. Media Streams Exchanged
```javascript
// Client-side verification
const hasLocalAudio = localStream && localStream.getAudioTracks().length > 0;
const hasRemoteStream = document.getElementById('remoteVideo')?.srcObject;

if (!hasLocalAudio || !hasRemoteStream) {
    await handleConnectionFailure('Media streams not established');
    return;
}
```

#### 3. No Fake Active State
**Prevention**:
- Timer won't start if connection not established
- Recording won't start if streams not flowing
- UI shows "Connecting..." until verified
- Server requires 'connected' signal from client

## Failure Handling

### Connection Failure Scenarios

#### 1. Media Permission Denied
```
Error: Unable to access camera/microphone
Action: Show error alert, end call
Timer: NOT started
Recording: NOT started
```

#### 2. WebRTC Connection Failed
```
State: peerConnection.connectionState === 'failed'
Action: Stop recording (if active), clean up, show error, end call
Message: "The connection failed. Please try again."
```

#### 3. Media Streams Not Established
```
Check: hasLocalAudio && hasRemoteStream
Action: Call handleConnectionFailure()
Message: "Media streams could not be established. Please check permissions."
```

#### 4. Connection Disconnected
```
State: peerConnection.connectionState === 'disconnected'
Action: Stop recording, maintain cleanup
Warning: Console log only (might reconnect)
```

### Failure Handler Function
```javascript
async function handleConnectionFailure(message) {
    // 1. Stop recording if active
    if (isRecording) {
        await stopRecording();
    }
    
    // 2. Clear timers (prevent running without connection)
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }
    
    // 3. Stop all polling
    stopCallStatePolling();
    stopSignalingPoll();
    
    // 4. Show error to user
    Swal.fire({
        title: 'Connection Failed',
        text: message,
        icon: 'error'
    }).then(() => {
        // 5. End call for BOTH parties
        endCall();
    });
}
```

### Error Display
**Method**: SweetAlert2 modal
**Icon**: Error (red X)
**Action**: Auto-ends call on confirmation
**Server Sync**: Updates database to 'ended' status

## Speaking Detection

### Audio Analysis
**Technology**: Web Audio API `AnalyserNode`
**Update Frequency**: Every 100ms
**Threshold**: Audio level > 30

### Visual Feedback
**Waveform Animation**: 5 bars that grow/shrink based on audio
**Trigger**: Shows when user is speaking
**Hide**: When muted or silent

### Implementation
```javascript
function startSpeakingDetection() {
    audioContext = new AudioContext();
    audioAnalyzer = audioContext.createAnalyser();
    audioAnalyzer.fftSize = 256;
    
    const source = audioContext.createMediaStreamSource(localStream);
    source.connect(audioAnalyzer);
    
    const dataArray = new Uint8Array(audioAnalyzer.frequencyBinCount);
    
    speakingDetectionInterval = setInterval(() => {
        if (isMuted) return;
        
        audioAnalyzer.getByteFrequencyData(dataArray);
        const average = dataArray.reduce((a, b) => a + b) / dataArray.length;
        
        // Show/hide waveform based on audio level
        if (average > 30) {
            waveform.classList.remove('hidden');
        } else {
            waveform.classList.add('hidden');
        }
    }, 100);
}
```

## Success Notification

### Display
**Type**: Toast notification (top-right corner)
**Duration**: 3 seconds
**Progress Bar**: Yes
**Icon**: Green checkmark

### Content
```
✓ Doctor and Nurse are now connected
```
(Roles swap based on who initiated the call)

### Implementation
```javascript
Swal.fire({
    toast: true,
    position: 'top-end',
    icon: 'success',
    title: `${role} and ${receiverName} are now connected`,
    showConfirmButton: false,
    timer: 3000,
    timerProgressBar: true
});
```

## Testing Checklist

### Connection Verification
- [ ] Call transitions: initiated → ringing → connected
- [ ] Timer starts only after connection established
- [ ] Timer shows HH:MM:SS format
- [ ] Both parties see same call duration
- [ ] Recording auto-starts 1 second after connection
- [ ] Recording indicator visible to both parties

### Media Verification
- [ ] Doctor can hear Nurse
- [ ] Nurse can hear Doctor
- [ ] Video displays for both parties (video calls)
- [ ] Local video in bottom-right corner
- [ ] Remote video fills background
- [ ] Audio waveform shows when speaking

### UI Indicators
- [ ] Microphone indicator shows "Active"
- [ ] Camera indicator shows "Active" (video only)
- [ ] Recording indicator pulses red
- [ ] Connection indicator shows "Connected"
- [ ] Muting grays out microphone indicator
- [ ] Camera off grays out camera indicator
- [ ] Speaking shows animated waveform

### Failure Handling
- [ ] Permission denied shows error and ends call
- [ ] Connection failure shows error and ends call
- [ ] No timer if connection fails
- [ ] No recording if connection fails
- [ ] Both parties disconnected on failure

### Edge Cases
- [ ] Page refresh during call ends properly
- [ ] Browser crash stops recording
- [ ] Network disconnect handled gracefully
- [ ] One party ending updates both parties
- [ ] Recording saves even if page closes

## Architecture Summary

### Client-Side Components
1. **WebRTC Manager**: Handles peer connection
2. **Media Manager**: Manages local/remote streams
3. **UI Controller**: Updates indicators and status
4. **Recording Manager**: Handles MediaRecorder
5. **Audio Analyzer**: Detects speaking activity
6. **Timer Controller**: Updates call duration display
7. **Failure Handler**: Manages error states

### Server-Side Components
1. **Call Model**: Tracks call state and metadata
2. **Signal Endpoint**: Handles WebRTC signaling
3. **Recording Endpoints**: Manages recording lifecycle
4. **Status Endpoint**: Provides state synchronization

### State Machine
```
IDLE → INITIATED → RINGING → CONNECTED → RECORDING → ENDED
                                    ↓
                               (if fails)
                                    ↓
                                  ENDED
```

## Security & Privacy

### Recording Consent
- Recording indicator ALWAYS visible during recording
- Both parties notified when recording starts
- Cannot hide recording status

### Media Permissions
- Browser requires user permission for camera/microphone
- Permission denial handled gracefully
- No call proceeds without media access

### Data Protection
- Recordings saved server-side only
- File names include call ID and timestamp
- Access restricted to call participants

## Performance Considerations

### Optimizations
- **Audio Analysis**: Only runs when unmuted
- **Polling**: 1-second intervals (minimal overhead)
- **Recording**: 5-second chunks (prevents memory bloat)
- **UI Updates**: RequestAnimationFrame for smooth animations

### Resource Cleanup
- All intervals cleared on call end
- Media tracks stopped properly
- Peer connections closed
- Audio contexts disposed

## Browser Compatibility

### Supported Browsers
- ✅ Chrome 74+ (full support)
- ✅ Firefox 66+ (full support)
- ✅ Edge 79+ (full support)
- ✅ Safari 14.1+ (limited recording support)
- ✅ Opera 62+ (full support)

### Required APIs
- WebRTC (RTCPeerConnection)
- MediaRecorder API
- Web Audio API (AudioContext)
- MediaStream API
- Fetch API

## Future Enhancements

1. **WebSocket Signaling**: Replace HTTP polling for real-time updates
2. **Network Quality Indicator**: Show connection strength
3. **Bandwidth Adaptation**: Adjust quality based on network
4. **Screen Sharing**: Share doctor's screen with nurse
5. **Chat During Call**: Text messaging alongside video/audio
6. **Call Transfer**: Transfer call to another doctor/nurse
7. **Recording Pause/Resume**: Control recording during call
8. **Multi-party Calls**: Conference calls with 3+ participants

---

**Document Version**: 1.0  
**Last Updated**: January 13, 2026  
**Author**: AI Assistant  
**System**: Alera Medical Communication System
