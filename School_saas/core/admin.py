# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import School, SchoolClass, Subject, Student, Score, CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('username', 'email')


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'created_at')
    search_fields = ('name',)


@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'school', 'year')
    list_filter = ('school', 'year')
    search_fields = ('name',)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'school')
    search_fields = ('name', 'code')


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('admission_number', 'first_name', 'last_name', 'school', 'school_class', 'gender')
    list_filter = ('school', 'school_class', 'gender')
    search_fields = ('admission_number', 'first_name', 'last_name')


@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'term', 'session', 'score', 'recorded_by', 'date_recorded')
    list_filter = ('term', 'session', 'subject')
    search_fields = ('student__admission_number', 'student__first_name', 'student__last_name')

