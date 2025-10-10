from django.urls import path
from . import views

app_name = 'knowledge'

urlpatterns = [
    path('', views.knowledge_base_dashboard, name='dashboard'),
    path('documents/', views.document_list, name='document_list'),
    path('documents/<int:pk>/', views.document_detail, name='document_detail'),
    path('upload/', views.document_upload, name='document_upload'),
    path('search/', views.search_knowledge, name='search'),
]
