from django import forms
from .models import Student, Subject, Score, SchoolClass

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'first_name',
            'last_name',
            'admission_number',
            'gender',
            'date_of_birth',
            'school',
            'school_class'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }

class SchoolClassForm(forms.ModelForm):
    class Meta:
        model = SchoolClass
        fields = ['name', 'year']


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'code', 'school']

class ScoreForm(forms.ModelForm):
    class Meta:
        model = Score
        fields = ['student', 'subject', 'term', 'session', 'score', 'max_score']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # get current user from view
        super().__init__(*args, **kwargs)

        # Filter student and subject fields by user’s school
        if user and user.school:
            self.fields['student'].queryset = Student.objects.filter(school=user.school)
            self.fields['subject'].queryset = Subject.objects.filter(school=user.school)
