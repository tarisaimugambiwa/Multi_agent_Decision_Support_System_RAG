from django.db import models
from django.conf import settings
from django.utils import timezone

class Conversation(models.Model):
    """Represents a conversation between users"""
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        participants_names = ', '.join([user.username for user in self.participants.all()[:2]])
        return f"Conversation: {participants_names}"
    
    def get_last_message(self):
        return self.messages.first()
    
    def get_unread_count(self, user):
        return self.messages.filter(is_read=False).exclude(sender=user).count()

class Message(models.Model):
    """Represents a message in a conversation"""
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.sender.username}: {self.content[:30]}"
    
    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()

class Call(models.Model):
    """Represents a voice or video call between users"""
    CALL_TYPE_CHOICES = [
        ('voice', 'Voice Call'),
        ('video', 'Video Call'),
    ]
    
    STATUS_CHOICES = [
        ('initiated', 'Initiated'),
        ('ringing', 'Ringing'),
        ('active', 'Active'),
        ('ongoing', 'Ongoing'),
        ('ended', 'Ended'),
        ('missed', 'Missed'),
        ('declined', 'Declined'),
    ]
    
    caller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='calls_made')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='calls_received')
    call_type = models.CharField(max_length=10, choices=CALL_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='initiated')
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    duration = models.IntegerField(null=True, blank=True, help_text="Duration in seconds")
    room_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    
    # WebRTC signaling fields
    caller_offer = models.TextField(null=True, blank=True, help_text="SDP offer from caller")
    receiver_answer = models.TextField(null=True, blank=True, help_text="SDP answer from receiver")
    ice_candidates = models.TextField(null=True, blank=True, help_text="JSON array of ICE candidates")
    
    class Meta:
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.call_type} call from {self.caller.username} to {self.receiver.username}"
    
    def end_call(self):
        self.status = 'ended'
        self.ended_at = timezone.now()
        if self.started_at:
            self.duration = int((self.ended_at - self.started_at).total_seconds())
        self.save()
