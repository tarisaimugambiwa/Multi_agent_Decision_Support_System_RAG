from django.urls import path
from . import views

app_name = 'communications'

urlpatterns = [
    path('inbox/', views.messages_inbox, name='inbox'),
    path('conversation/<int:conversation_id>/', views.conversation_detail, name='conversation_detail'),
    path('conversation/<int:conversation_id>/send/', views.send_message, name='send_message'),
    path('conversation/<int:conversation_id>/messages/', views.get_new_messages, name='get_new_messages'),
    path('start/<int:user_id>/', views.start_conversation, name='start_conversation'),
    path('users/', views.user_list, name='user_list'),
    # Specific call patterns must come before the generic initiate_call pattern
    path('call/<int:call_id>/answer/', views.answer_call, name='answer_call'),
    path('call/<int:call_id>/decline/', views.decline_call, name='decline_call'),
    path('call/<int:call_id>/end/', views.end_call, name='end_call'),
    path('call/<int:call_id>/status/', views.call_status, name='call_status'),
    path('call/<int:call_id>/signal/', views.webrtc_signal, name='webrtc_signal'),
    path('call/<int:call_id>/recording/start/', views.start_recording, name='start_recording'),
    path('call/<int:call_id>/recording/stop/', views.stop_recording, name='stop_recording'),
    path('call/<int:call_id>/recording/save/', views.save_recording_chunk, name='save_recording_chunk'),
    # Generic pattern for initiating calls (must be after specific patterns)
    path('call/<int:user_id>/<str:call_type>/', views.initiate_call, name='initiate_call'),
    path('check-incoming-calls/', views.check_incoming_calls, name='check_incoming_calls'),
    path('get-missed-calls-count/', views.get_missed_calls_count, name='get_missed_calls_count'),
    path('missed-calls/', views.missed_calls, name='missed_calls'),
]
