from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import StudentForm, SubjectForm, ScoreForm, SchoolClassForm
from .models import Student, Subject, Score, School, CustomUser as User
from django.db import transaction


from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from .models import CustomUser as User, School

def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        role = request.POST.get("role", "teacher")  # default to teacher
        school_name = request.POST.get("school_name")

        # Validation
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect('register')

        if not school_name:
            messages.error(request, "School name is required.")
            return redirect('register')

        # Create or get school
        school, created = School.objects.get_or_create(name=school_name)

        # Create user under that school
        with transaction.atomic():
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                role=role,
                school=school
            )

        messages.success(request, "Registration successful! You can now log in.")
        return redirect('login')

    return render(request, 'accounts/register.html')


# -----------------------
# BASIC PAGES
# -----------------------

@login_required
def dashboard(request):
    user = request.user
    students = Student.objects.filter(school=user.school)
    subjects = Subject.objects.filter(school=user.school)
    context = {
        'user': user,
        'students_count': students.count(),
        'subjects_count': subjects.count(),
    }
    return render(request, 'core/dashboard.html', context)

def home(request):
    return render(request, 'core/home.html')

@login_required
def students(request):
    students = Student.objects.filter(school=request.user.school)
    return render(request, 'core/students.html', {'students': students})

@login_required
def classes(request):
    return render(request, 'core/classes.html')

@login_required
def teachers_view(request):
    return render(request, 'core/teachers.html')


# -----------------------
# STUDENT CRUD
# -----------------------

@login_required(login_url='login')
def add_student(request):
    form = StudentForm()
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save(commit=False)
            student.school = request.user.school
            student.save()
            messages.success(request, 'Student added successfully!')
            return redirect('students')
    return render(request, 'core/add_student.html', {'form': form})

@login_required(login_url='login')
def edit_student(request, pk):
    student = get_object_or_404(Student, pk=pk, school=request.user.school)
    form = StudentForm(instance=student)
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student updated successfully!')
            return redirect('students')
    return render(request, 'core/add_student.html', {'form': form})

@login_required(login_url='login')
def delete_student(request, pk):
    student = get_object_or_404(Student, pk=pk, school=request.user.school)
    student.delete()
    messages.success(request, 'Student deleted successfully!')
    return redirect('students')

# -----------------------
# SUBJECT CRUD
# -----------------------

@login_required(login_url='login')
def add_subject(request):
    form = SubjectForm()
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            subject = form.save(commit=False)
            subject.school = request.user.school
            subject.save()
            messages.success(request, 'Subject added successfully!')
            return redirect('subjects')
    return render(request, 'core/add_subject.html', {'form': form})


@login_required(login_url='login')
def subjects(request):
    subjects = Subject.objects.filter(school=request.user.school)
    return render(request, 'core/subjects.html', {'subjects': subjects})


@login_required(login_url='login')
def edit_subject(request, pk):
    subject = get_object_or_404(Subject, pk=pk, school=request.user.school)
    form = SubjectForm(instance=subject)
    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=subject)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subject updated successfully!')
            return redirect('subjects')
    return render(request, 'core/add_subject.html', {'form': form})


@login_required(login_url='login')
def delete_subject(request, pk):
    subject = get_object_or_404(Subject, pk=pk, school=request.user.school)
    subject.delete()
    messages.success(request, 'Subject deleted successfully!')
    return redirect('subjects')

# -----------------------
# CLASS CRUD
# -----------------------

from .models import SchoolClass

@login_required(login_url='login')
def classes(request):
    school_classes = SchoolClass.objects.filter(school=request.user.school)
    return render(request, 'core/classes.html', {'classes': school_classes})


@login_required(login_url='login')
def add_class(request):
    form = SchoolClassForm()
    if request.method == 'POST':
        form = SchoolClassForm(request.POST)
        if form.is_valid():
            school_class = form.save(commit=False)
            school_class.school = request.user.school
            school_class.save()
            messages.success(request, 'Class added successfully!')
            return redirect('classes')
    return render(request, 'core/add_class.html', {'form': form})


@login_required(login_url='login')
def edit_class(request, pk):
    school_class = get_object_or_404(SchoolClass, pk=pk, school=request.user.school)
    form = SchoolClassForm(instance=school_class)
    if request.method == 'POST':
        form = SchoolClassForm(request.POST, instance=school_class)
        if form.is_valid():
            form.save()
            messages.success(request, 'Class updated successfully!')
            return redirect('classes')
    return render(request, 'core/add_class.html', {'form': form})


@login_required(login_url='login')
def delete_class(request, pk):
    school_class = get_object_or_404(SchoolClass, pk=pk, school=request.user.school)
    school_class.delete()
    messages.success(request, 'Class deleted successfully!')
    return redirect('classes')

# --- SCORE CRUD ---
@login_required(login_url='login')
def add_score(request):
    form = ScoreForm(user=request.user)

    if request.method == 'POST':
        form = ScoreForm(request.POST, user=request.user)
        if form.is_valid():
            score = form.save(commit=False)
            score.recorded_by = request.user
            score.save()
            messages.success(request, 'Score recorded successfully!')
            return redirect('dashboard')

    return render(request, 'core/add_score.html', {'form': form})


@login_required(login_url='login')
def edit_score(request, pk):
    score = Score.objects.get(id=pk)
    form = ScoreForm(instance=score, user=request.user)

    if request.method == 'POST':
        form = ScoreForm(request.POST, instance=score, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Score updated successfully!')
            return redirect('dashboard')

    return render(request, 'core/add_score.html', {'form': form})


@login_required(login_url='login')
def delete_score(request, pk):
    score = Score.objects.get(id=pk)
    score.delete()
    messages.success(request, 'Score deleted successfully!')
    return redirect('dashboard')