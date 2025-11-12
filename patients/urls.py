"""
URL configuration for patients app.
"""

from django.urls import path
from . import views

app_name = 'patients'

urlpatterns = [
    # View for the search page
    path('search/', views.patient_search_view, name='patient_search'),
    
    # API endpoint for search
    path('api/search/', views.patient_search_api, name='patient_search_api'),
    
    # Patient detail view
    path('<int:pk>/', views.PatientDetailView.as_view(), name='patient_detail'),
    
    # Patient management URLs
    path('', views.PatientListView.as_view(), name='patient_list'),
    path('create/', views.PatientCreateView.as_view(), name='patient_create'),
    path('<int:pk>/edit/', views.PatientUpdateView.as_view(), name='patient_update'),
    path('<int:pk>/delete/', views.PatientDeleteView.as_view(), name='patient_delete'),
    
    # Medical Records URLs
    path('records/', views.MedicalRecordListView.as_view(), name='medical_record_list'),
    path('records/create/', views.MedicalRecordCreateView.as_view(), name='medical_record_create'),
    path('records/<int:pk>/', views.MedicalRecordDetailView.as_view(), name='medical_record_detail'),
    
    # API endpoints
    path('api/recent/', views.recent_patients_api, name='recent_patients_api'),
    path('api/<int:patient_id>/detail/', views.patient_detail_api, name='patient_detail_api'),
    path('api/stats/', views.dashboard_stats_api, name='dashboard_stats_api'),
    # Patient portal
    path('dashboard/', views.patient_dashboard, name='patient_dashboard'),
    # Patient signup (self-registration)
    path('signup/', views.patient_signup, name='patient_signup'),
]