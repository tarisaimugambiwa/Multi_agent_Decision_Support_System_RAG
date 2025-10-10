"""
URL configuration for patients app.
"""

from django.urls import path
from . import views

app_name = 'patients'

urlpatterns = [
    # Main views
    path('search/', views.patient_search_view, name='patient_search'),
    
    # Patient management URLs
    path('', views.PatientListView.as_view(), name='patient_list'),
    path('create/', views.PatientCreateView.as_view(), name='patient_create'),
    path('<int:pk>/', views.PatientDetailView.as_view(), name='patient_detail'),
    path('<int:pk>/edit/', views.PatientUpdateView.as_view(), name='patient_update'),
    path('<int:pk>/delete/', views.PatientDeleteView.as_view(), name='patient_delete'),
    
    # Medical Records URLs
    path('records/', views.MedicalRecordListView.as_view(), name='medical_record_list'),
    path('records/create/', views.MedicalRecordCreateView.as_view(), name='medical_record_create'),
    path('records/<int:pk>/', views.MedicalRecordDetailView.as_view(), name='medical_record_detail'),
    
    # API endpoints
    path('api/search/', views.patient_search_api, name='patient_search_api'),
    path('api/recent/', views.recent_patients_api, name='recent_patients_api'),
    path('api/<int:patient_id>/detail/', views.patient_detail_api, name='patient_detail_api'),
    path('api/stats/', views.dashboard_stats_api, name='dashboard_stats_api'),
]