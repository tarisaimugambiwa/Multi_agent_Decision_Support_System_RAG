from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Max
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import Conversation, Message, Call
import uuid

User = get_user_model()

@login_required
def messages_inbox(request):
    """Display all conversations for the logged-in user"""
    conversations = Conversation.objects.filter(
        participants=request.user
    ).annotate(
        last_message_time=Max('messages__created_at')
    ).order_by('-last_message_time')
    
    # Get unread counts
    for conversation in conversations:
        conversation.unread_count = conversation.get_unread_count(request.user)
        conversation.last_message = conversation.get_last_message()
        conversation.other_user = conversation.participants.exclude(id=request.user.id).first()
    
    # Get missed calls count (only unviewed)
    missed_calls_count = Call.objects.filter(
        receiver=request.user,
        status='missed',
        is_viewed=False  # Only count unviewed missed calls
    ).count()
    
    context = {
        'conversations': conversations,
        'missed_calls_count': missed_calls_count,
    }
    return render(request, 'communications/inbox.html', context)

@login_required
def conversation_detail(request, conversation_id):
    """Display a specific conversation"""
    conversation = get_object_or_404(
        Conversation,
        id=conversation_id,
        participants=request.user
    )
    
    # Mark all messages as read
    conversation.messages.exclude(sender=request.user).filter(is_read=False).update(
        is_read=True,
        read_at=timezone.now()
    )
    
    messages = conversation.messages.all().order_by('created_at')
    other_user = conversation.participants.exclude(id=request.user.id).first()
    
    context = {
        'conversation': conversation,
        'messages': messages,
        'other_user': other_user,
    }
    return render(request, 'communications/conversation.html', context)

@login_required
def send_message(request, conversation_id):
    """Send a message in a conversation"""
    if request.method == 'POST':
        conversation = get_object_or_404(
            Conversation,
            id=conversation_id,
            participants=request.user
        )
        
        content = request.POST.get('content', '').strip()
        if content:
            message = Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=content
            )
            
            conversation.updated_at = timezone.now()
            conversation.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': {
                        'id': message.id,
                        'content': message.content,
                        'sender': message.sender.username,
                        'created_at': message.created_at.strftime('%I:%M %p'),
                    }
                })
        
        return redirect('communications:conversation_detail', conversation_id=conversation_id)
    
    return redirect('communications:inbox')

@login_required
def start_conversation(request, user_id):
    """Start a new conversation with a user"""
    other_user = get_object_or_404(User, id=user_id)
    
    # Check if conversation already exists
    existing_conversation = Conversation.objects.filter(
        participants=request.user
    ).filter(
        participants=other_user
    ).first()
    
    if existing_conversation:
        return redirect('communications:conversation_detail', conversation_id=existing_conversation.id)
    
    # Create new conversation
    conversation = Conversation.objects.create()
    conversation.participants.add(request.user, other_user)
    
    return redirect('communications:conversation_detail', conversation_id=conversation.id)

@login_required
def get_new_messages(request, conversation_id):
    """Get new messages for a conversation (AJAX endpoint)"""
    conversation = get_object_or_404(
        Conversation,
        id=conversation_id,
        participants=request.user
    )
    
    last_message_id = request.GET.get('last_message_id', 0)
    
    new_messages = conversation.messages.filter(
        id__gt=last_message_id
    ).order_by('created_at')
    
    messages_data = [{
        'id': msg.id,
        'content': msg.content,
        'sender': msg.sender.username,
        'sender_id': msg.sender.id,
        'created_at': msg.created_at.strftime('%I:%M %p'),
        'is_own': msg.sender.id == request.user.id,
    } for msg in new_messages]
    
    # Mark messages as read
    new_messages.exclude(sender=request.user).update(
        is_read=True,
        read_at=timezone.now()
    )
    
    return JsonResponse({'messages': messages_data})

@login_required
def user_list(request):
    """List all users for starting conversations"""
    users = User.objects.exclude(id=request.user.id).filter(
        is_active=True
    ).order_by('username')
    
    # If user is a patient, only show nurses and doctors
    if request.user.role == 'PATIENT':
        users = users.filter(role__in=['NURSE', 'DOCTOR'])
    
    # Add role filter
    role_filter = request.GET.get('role')
    if role_filter:
        users = users.filter(role=role_filter)
    
    context = {
        'users': users,
    }
    return render(request, 'communications/user_list.html', context)

@login_required
@login_required
def initiate_call(request, user_id, call_type):
    """
    Initiate a voice or video call
    - Creates call record with 'initiated' status
    - Receiver will see incoming call notification
    """
    receiver = get_object_or_404(User, id=user_id)
    
    # Create call record with 'initiated' status so receiver gets notification
    room_id = str(uuid.uuid4())
    call = Call.objects.create(
        caller=request.user,
        receiver=receiver,
        call_type=call_type,
        status='initiated',
        room_id=room_id
    )
    
    print(f"[Initiate Call] {request.user.username} calling {receiver.username}, "
          f"Call ID: {call.id}, Type: {call_type}")
    
    context = {
        'call': call,
        'receiver': receiver,
        'room_id': room_id,
        'is_receiver': False
    }
    return render(request, 'communications/call.html', context)
@login_required
def end_call(request, call_id):
    """
    End an ongoing call - SERVER AUTHORITATIVE
    - Updates call status to 'ended'
    - Records end time and duration
    - Marks as 'missed' if never answered
    - Stops recording if active
    - Broadcasts termination to both participants
    """
    call = get_object_or_404(
        Call,
        Q(caller=request.user) | Q(receiver=request.user),
        id=call_id
    )
    
    print(f"[End Call] User {request.user.username} ending call {call_id}, current status: {call.status}")
    
    # Prevent double-ending
    if call.status in ['ended', 'declined', 'missed']:
        print(f"[End Call] Call {call_id} already terminated with status: {call.status}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'already_ended': True,
                'status': call.status
            })
        return redirect('communications:inbox')
    
    # Determine termination type
    termination_type = None
    
    # Mark as missed if never answered (still in initiated/ringing status)
    if call.status in ['initiated', 'ringing']:
        call.status = 'missed'
        call.ended_at = timezone.now()
        call.save()
        termination_type = 'missed'
        print(f"[End Call] Call {call_id} marked as missed")
    else:
        # Normal call end - use the model method (stops recording automatically)
        call.end_call()
        termination_type = 'ended'
        print(f"[End Call] Call {call_id} ended normally, duration: {call.duration}s")
    
    # Return termination event to trigger cleanup on client
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'status': call.status,
            'termination_type': termination_type,
            'ended_at': call.ended_at.isoformat() if call.ended_at else None,
            'duration': call.duration
        })
    
    return redirect('communications:inbox')

@login_required
def missed_calls(request):
    """Display missed calls for the current user"""
    # Get missed calls where user is the receiver
    calls = Call.objects.filter(
        receiver=request.user,
        status='missed'
    ).select_related('caller').order_by('-started_at')
    
    # Mark all missed calls as viewed when user opens this page
    Call.objects.filter(
        receiver=request.user,
        status='missed',
        is_viewed=False
    ).update(is_viewed=True)
    
    context = {
        'calls': calls,
    }
    return render(request, 'communications/missed_calls.html', context)

@login_required
def check_incoming_calls(request):
    """Check for incoming calls for the current user"""
    from datetime import timedelta
    
    # Only check for current calls from the last 60 seconds (covers full call timeout period)
    time_threshold = timezone.now() - timedelta(seconds=60)
    
    incoming_call = Call.objects.filter(
        receiver=request.user,
        status='initiated',
        started_at__gte=time_threshold
    ).select_related('caller').first()
    
    if incoming_call:
        return JsonResponse({
            'has_call': True,
            'call_id': incoming_call.id,
            'caller_name': incoming_call.caller.get_full_name() or incoming_call.caller.username,
            'caller_role': incoming_call.caller.get_role_display(),
            'call_type': incoming_call.call_type,
        })
    return JsonResponse({'has_call': False})

@login_required
def answer_call(request, call_id):
    """Answer an incoming call"""
    from datetime import timedelta
    
    # Only allow answering current calls from the last 60 seconds
    time_threshold = timezone.now() - timedelta(seconds=60)
    
    try:
        # Allow answering calls that are either 'initiated' or 'ringing' status
        # (ringing status is set when caller sends offer)
        call = Call.objects.get(
            id=call_id, 
            receiver=request.user, 
            status__in=['initiated', 'ringing'],
            started_at__gte=time_threshold
        )
    except Call.DoesNotExist:
        # Call no longer available
        messages.error(request, 'This call is no longer available.')
        print(f"[Answer Call] Call {call_id} not found or not available for user {request.user.username}")
        return redirect('communications:inbox')
    
    # Update status to ringing if it was still initiated
    if call.status == 'initiated':
        call.status = 'ringing'
        call.save()
    
    print(f"[Answer Call] User {request.user.username} answering call {call_id}")
    
    return render(request, 'communications/call.html', {
        'call': call,
        'receiver': call.caller,  # For receiver, the other user is the caller
        'is_receiver': True
    })

@login_required
def decline_call(request, call_id):
    """Decline an incoming call"""
    call = get_object_or_404(Call, id=call_id, receiver=request.user)
    call.status = 'declined'
    call.ended_at = timezone.now()
    call.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    return redirect('communications:inbox')

@login_required
def call_status(request, call_id):
    """
    Get current call status - SERVER AUTHORITATIVE
    Used for polling to detect when the other party ends the call
    Also detects timeout/stale calls and auto-terminates them
    """
    from datetime import timedelta
    
    call = get_object_or_404(
        Call,
        Q(caller=request.user) | Q(receiver=request.user),
        id=call_id
    )
    
    # Auto-terminate stale calls (active for more than 2 hours without proper end)
    if call.status in ['initiated', 'ringing', 'connected', 'recording']:
        time_elapsed = timezone.now() - call.started_at
        if time_elapsed > timedelta(hours=2):
            print(f"[Call Status] Auto-terminating stale call {call_id}, elapsed: {time_elapsed}")
            call.end_call()
    
    # Get other participant info for disconnect detection
    other_participant = call.receiver if request.user == call.caller else call.caller
    
    return JsonResponse({
        'status': call.status,
        'is_recording': call.is_recording,
        'ended_at': call.ended_at.isoformat() if call.ended_at else None,
        'duration': call.duration,
        'is_terminated': call.status in ['ended', 'declined', 'missed'],
        'other_participant': other_participant.get_full_name() or other_participant.username
    })

@login_required
def start_recording(request, call_id):
    """
    Start call recording
    - Only allowed when call is in 'connected' state
    - Automatically starts recording when both parties are connected
    """
    call = get_object_or_404(
        Call,
        Q(caller=request.user) | Q(receiver=request.user),
        id=call_id
    )
    
    if call.status != 'connected':
        return JsonResponse({
            'success': False,
            'error': 'Call must be connected before recording can start'
        }, status=400)
    
    if call.start_recording():
        print(f"[Call {call_id}] Recording started by {request.user.username}")
        return JsonResponse({
            'success': True,
            'status': 'recording',
            'recording_started_at': call.recording_started_at.isoformat()
        })
    else:
        return JsonResponse({
            'success': False,
            'error': 'Recording already in progress'
        }, status=400)

@login_required
def stop_recording(request, call_id):
    """
    Stop call recording
    - Can be called manually or automatically when call ends
    """
    call = get_object_or_404(
        Call,
        Q(caller=request.user) | Q(receiver=request.user),
        id=call_id
    )
    
    if call.stop_recording():
        print(f"[Call {call_id}] Recording stopped by {request.user.username}, "
              f"Duration: {call.recording_duration}s")
        return JsonResponse({
            'success': True,
            'recording_duration': call.recording_duration,
            'recording_ended_at': call.recording_ended_at.isoformat()
        })
    else:
        return JsonResponse({
            'success': False,
            'error': 'No active recording'
        }, status=400)

@login_required
def save_recording_chunk(request, call_id):
    """
    Save recording data chunks from client
    - Receives MediaRecorder blob chunks
    - Stores them for the call recording
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    call = get_object_or_404(
        Call,
        Q(caller=request.user) | Q(receiver=request.user),
        id=call_id
    )
    
    # Create recordings directory if it doesn't exist
    import os
    from django.conf import settings
    recordings_dir = os.path.join(settings.MEDIA_ROOT, 'call_recordings')
    os.makedirs(recordings_dir, exist_ok=True)
    
    # Generate filename
    filename = f"call_{call_id}_{request.user.id}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.webm"
    filepath = os.path.join(recordings_dir, filename)
    
    # Save the uploaded chunk
    try:
        if 'audio_data' in request.FILES:
            chunk = request.FILES['audio_data']
            with open(filepath, 'ab') as f:  # Append mode
                for chunk_data in chunk.chunks():
                    f.write(chunk_data)
            
            # Update call record with file path
            if not call.recording_file_path:
                call.recording_file_path = filepath
                call.save()
            
            return JsonResponse({'success': True, 'filename': filename})
    except Exception as e:
        print(f"[Call {call_id}] Error saving recording chunk: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    return JsonResponse({'success': False, 'error': 'No audio data'}, status=400)

@login_required
def get_missed_calls_count(request):
    """Get the count of unviewed missed calls for the current user"""
    missed_calls_count = Call.objects.filter(
        receiver=request.user,
        status='missed',
        is_viewed=False  # Only count unviewed missed calls
    ).count()
    
    return JsonResponse({
        'count': missed_calls_count
    })

@login_required
@login_required
def webrtc_signal(request, call_id):
    """Handle WebRTC signaling (SDP offer/answer and ICE candidates)"""
    call = get_object_or_404(
        Call,
        Q(caller=request.user) | Q(receiver=request.user),
        id=call_id
    )
    
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        
        if data.get('type') == 'offer':
            call.caller_offer = data.get('sdp')
            call.status = 'ringing'
            call.save()
            print(f"[Call {call_id}] Offer saved from caller - status: ringing")
            return JsonResponse({'success': True})
        
        elif data.get('type') == 'answer':
            call.receiver_answer = data.get('sdp')
            # Don't change to recording yet - wait for connected state
            call.status = 'connected'
            call.connected_at = timezone.now()
            call.save()
            print(f"[Call {call_id}] Answer saved from receiver - status: connected")
            return JsonResponse({'success': True})
        
        elif data.get('type') == 'ice-candidate':
            candidate = data.get('candidate')
            if candidate:
                candidates = json.loads(call.ice_candidates or '[]')
                # Add role information to track which peer sent the candidate
                candidate['from_caller'] = (request.user == call.caller)
                candidates.append(candidate)
                call.ice_candidates = json.dumps(candidates)
                call.save()
                print(f"[Call {call_id}] ICE candidate added from {'caller' if request.user == call.caller else 'receiver'}")
            return JsonResponse({'success': True})
        
        elif data.get('type') == 'connected':
            # Client confirms WebRTC connection established
            if call.mark_connected():
                print(f"[Call {call_id}] Marked as connected by {request.user.username}")
                return JsonResponse({'success': True, 'status': 'connected'})
    
    # GET request - retrieve signaling data for the other peer
    import json
    all_candidates = json.loads(call.ice_candidates or '[]')
    
    # Filter candidates: send only candidates from the OTHER peer
    is_caller = (request.user == call.caller)
    filtered_candidates = [
        c for c in all_candidates 
        if c.get('from_caller') != is_caller  # Get candidates from the other peer
    ]
    
    print(f"[Call {call_id}] GET signal - User: {'caller' if is_caller else 'receiver'}, "
          f"Offer: {'Yes' if call.caller_offer else 'No'}, "
          f"Answer: {'Yes' if call.receiver_answer else 'No'}, "
          f"ICE candidates: {len(filtered_candidates)}, "
          f"Status: {call.status}")
    
    return JsonResponse({
        'offer': call.caller_offer,
        'answer': call.receiver_answer,
        'ice_candidates': filtered_candidates,
        'status': call.status,
        'is_recording': call.is_recording
    })
