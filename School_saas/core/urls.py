from django.urls import path
from core import views

urlpatterns = [
    path('teachers/', views.teachers_view, name='teachers'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('students/', views.students, name='students'),  
    path('classes/', views.classes, name='classes'),
]