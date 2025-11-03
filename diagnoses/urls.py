"""
URL Configuration for diagnoses app
"""

from django.urls import path
from . import views

app_name = 'diagnoses'

urlpatterns = [
    # Case management URLs
    path('', views.CaseListView.as_view(), name='case_list'),
    path('create/', views.CaseCreateView.as_view(), name='case_create'),
    path('<int:pk>/', views.CaseDetailView.as_view(), name='case_detail'),
    path('<int:pk>/review/', views.CaseReviewView.as_view(), name='case_review'),
    
    # AJAX endpoints
    path('ajax/patient-history/<int:patient_id>/', 
         views.get_patient_history_ajax, 
         name='patient_history_ajax'),
    path('ajax/quick-triage/', 
         views.quick_triage_ajax, 
         name='quick_triage_ajax'),
    path('api/search-patients/', views.search_patients, name='search_patients'),
]