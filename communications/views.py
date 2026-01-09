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
    
    # Get missed calls count
    missed_calls_count = Call.objects.filter(
        receiver=request.user,
        status='missed'
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
    
    # Add role filter
    role_filter = request.GET.get('role')
    if role_filter:
        users = users.filter(role=role_filter)
    
    context = {
        'users': users,
    }
    return render(request, 'communications/user_list.html', context)

@login_required
def initiate_call(request, user_id, call_type):
    """Initiate a voice or video call"""
    receiver = get_object_or_404(User, id=user_id)
    
    # Create call record with 'initiated' status so receiver gets notification
    room_id = str(uuid.uuid4())
    call = Call.objects.create(
        caller=request.user,
        receiver=receiver,
        call_type=call_type,
        status='initiated',  # Changed from 'active' to 'initiated'
        room_id=room_id
    )
    
    context = {
        'call': call,
        'receiver': receiver,
        'room_id': room_id,
        'is_receiver': False
    }
    return render(request, 'communications/call.html', context)

@login_required
def end_call(request, call_id):
    """End an ongoing call"""
    call = get_object_or_404(
        Call,
        Q(caller=request.user) | Q(receiver=request.user),
        id=call_id
    )
    
    # Mark as missed if never answered (still in initiated/ringing status)
    if call.status in ['initiated', 'ringing']:
        call.status = 'missed'
        call.ended_at = timezone.now()
        call.save()
    else:
        # Normal call end
        call.end_call()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    return redirect('communications:inbox')

@login_required
def missed_calls(request):
    """Display missed calls for the current user"""
    # Get missed calls where user is the receiver
    calls = Call.objects.filter(
        receiver=request.user,
        status='missed'
    ).select_related('caller').order_by('-started_at')
    
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
        call = Call.objects.get(
            id=call_id, 
            receiver=request.user, 
            status='initiated',
            started_at__gte=time_threshold
        )
    except Call.DoesNotExist:
        # Call no longer available
        messages.error(request, 'This call is no longer available.')
        return redirect('communications:inbox')
    
    call.status = 'ringing'  # Mark as ringing when receiver answers
    call.save()
    
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
def get_missed_calls_count(request):
    """Get the count of missed calls for the current user"""
    missed_calls_count = Call.objects.filter(
        receiver=request.user,
        status='missed'
    ).count()
    
    return JsonResponse({
        'count': missed_calls_count
    })

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
            return JsonResponse({'success': True})
        
        elif data.get('type') == 'answer':
            call.receiver_answer = data.get('sdp')
            call.status = 'ongoing'
            call.save()
            return JsonResponse({'success': True})
        
        elif data.get('type') == 'ice-candidate':
            candidates = json.loads(call.ice_candidates or '[]')
            candidates.append(data.get('candidate'))
            call.ice_candidates = json.dumps(candidates)
            call.save()
            return JsonResponse({'success': True})
    
    # GET request - retrieve signaling data
    import json
    return JsonResponse({
        'offer': call.caller_offer,
        'answer': call.receiver_answer,
        'ice_candidates': json.loads(call.ice_candidates or '[]'),
        'status': call.status
    })
