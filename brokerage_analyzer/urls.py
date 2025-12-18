from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('upload/', views.upload_notes, name='upload_notes'),
    path('download/', views.download_report, name='download_report'),
]
