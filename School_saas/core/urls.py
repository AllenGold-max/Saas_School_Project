from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('teachers/', views.teacher_list, name='teacher_list'),
    path('filter-suggestions/', views.filter_suggestions, name='filter_suggestions'),
    path('dashboard/filter/', views.filter_dashboard, name='filter_dashboard'),
    path('filter_dashboard/', views.filter_dashboard, name='filter_dashboard'),
    path('filter_suggestions/', views.filter_suggestions, name='filter_suggestions'),  # 👈 add this
    path("import-data/", views.import_school_data, name="import_data"),

    # Students
    path('students/', views.students, name='students'),
    path('students/add/', views.add_student, name='add_student'),
    path('students/edit/<int:pk>/', views.edit_student, name='edit_student'),
    path('students/delete/<int:pk>/', views.delete_student, name='delete_student'),

    # Subjects
    path('subjects/', views.subjects, name='subjects'),
    path('subjects/add/', views.add_subject, name='add_subject'),
    path('subjects/edit/<int:pk>/', views.edit_subject, name='edit_subject'),
    path('subjects/delete/<int:pk>/', views.delete_subject, name='delete_subject'),

    # Classes
    path('classes/', views.classes, name='classes'),
    path('classes/add/', views.add_class, name='add_class'),
    path('classes/edit/<int:pk>/', views.edit_class, name='edit_class'),
    path('classes/delete/<int:pk>/', views.delete_class, name='delete_class'),

    # Scores
    path('scores/add/', views.add_score, name='add_score'),
    path('scores/edit/<int:pk>/', views.edit_score, name='edit_score'),
    path('scores/delete/<int:pk>/', views.delete_score, name='delete_score'),
]
