from django.urls import path
from . import views

app_name = 'patients'

urlpatterns = [
    path('', views.PatientListView.as_view(), name='patient_list'),
    path('create/', views.PatientCreateView.as_view(), name='patient_create'),
    path('<int:pk>/', views.PatientDetailView.as_view(), name='patient_detail'),
    path('<int:pk>/edit/', views.PatientUpdateView.as_view(), name='patient_update'),
    path('<int:pk>/delete/', views.PatientDeleteView.as_view(), name='patient_delete'),
    path('records/', views.MedicalRecordListView.as_view(), name='medical_record_list'),
    path('records/create/', views.MedicalRecordCreateView.as_view(), name='medical_record_create'),
    path('records/<int:pk>/', views.MedicalRecordDetailView.as_view(), name='medical_record_detail'),
    path('api/search/', views.patient_search_api, name='patient_search_api'),
    path('api/stats/', views.dashboard_stats_api, name='dashboard_stats_api'),
    path('nurse-dashboard/', views.nurse_dashboard, name='nurse_dashboard'),
]