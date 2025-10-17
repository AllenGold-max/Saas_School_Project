from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.db.models.functions import ExtractYear, Now
from django.db.models import Avg, Count


from .forms import StudentForm, SubjectForm, ScoreForm, SchoolClassForm
from .models import Student, Subject, Score, School, SchoolClass, CustomUser as User

def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        role = request.POST.get("role", "teacher")  # default to teacher
        school_name = request.POST.get("school_name")

        # --- Validation ---
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect('register')

        if not school_name:
            messages.error(request, "School name is required.")
            return redirect('register')

        # --- Normalize school name ---
        school_name = school_name.strip().title()  # ensures clean names like 'Great Minds School'

        # --- Create or reuse school ---
        school, _ = School.objects.get_or_create(name=school_name)

        # --- Create the user under that school ---
        with transaction.atomic():
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                role=role,
                school=school
            )

        messages.success(request, f"Registration successful under {school.name}! You can now log in.")
        return redirect('login')

    return render(request, 'accounts/register.html')



# -----------------------
# BASIC PAGES
# -----------------------

from django.db.models import Avg
from django.contrib.auth.decorators import login_required
from .models import Student, Subject, Score

@login_required
def dashboard(request):
    user = request.user
    school = user.school

    # Fetch school data
    students = Student.objects.filter(school=school)
    subjects = Subject.objects.filter(school=school)
    scores = Score.objects.filter(student__school=school)
    classes = SchoolClass.objects.filter(school=school)
    
    # 1️⃣ Class averages
    class_averages = (
        scores.values('student__school_class__name')
        .annotate(average_score=Avg('score'))
        .order_by('-average_score')
    )

    # 2️⃣ Top 5 students
    top_students = (
        scores.values('student__first_name', 'student__last_name')
        .annotate(average_score=Avg('score'))
        .order_by('-average_score')[:5]
    )

    # 3️⃣ Subject trends
    subject_trends = (
        scores.values('subject__name')
        .annotate(average_score=Avg('score'))
        .order_by('subject__name')
    )

    # ✅ Gender Distribution
    gender_data = (
        students.values('gender')
        .annotate(count=Count('gender'))
        .order_by('gender')
    )

    # ✅ Age Breakdown
    age_data = (
        students
        .annotate(age=ExtractYear(Now()) - ExtractYear('date_of_birth'))
        .values('age')
        .annotate(count=Count('age'))
        .order_by('age')
    )

    # ✅ Overall Performance by Class
    performance_by_class = (
        Score.objects.filter(student__school=school)
        .values('student__school_class__name')
        .annotate(average_score=Avg('score'))
        .order_by('student__school_class__name')
    )

    # 4️⃣ Personalized insights / suggestions
    suggestions = []
    for student in students:
        student_scores = scores.filter(student=student)
        if not student_scores.exists():
            continue  # skip if no scores yet

        avg_score = student_scores.aggregate(Avg('score'))['score__avg']

        if avg_score < 50:
            suggestions.append({
                'student': student,
                'type': 'alert',
                'message': f"{student.first_name} {student.last_name} is underperforming (average {avg_score:.1f}%). Consider extra lessons or follow-up."
            })
        elif avg_score < 70:
            suggestions.append({
                'student': student,
                'type': 'advice',
                'message': f"{student.first_name} {student.last_name} is doing fairly (average {avg_score:.1f}%). Encourage steady improvement."
            })
        else:
            suggestions.append({
                'student': student,
                'type': 'praise',
                'message': f"{student.first_name} {student.last_name} is performing excellently (average {avg_score:.1f}%)! Keep up the great work."
            })

    context = {
    'user': user,
    'students_count': students.count(),
    'subjects_count': subjects.count(),
    'class_averages': class_averages,
    'top_students': top_students,
    'subject_trends': subject_trends,
    'suggestions': suggestions,
    'classes': classes,  
    'gender_data': gender_data,
    'age_data': age_data,
    'performance_by_class': performance_by_class,
}


    return render(request, 'core/dashboard.html', context)

@login_required
def filter_suggestions(request):
    user = request.user
    school = user.school
    filter_type = request.GET.get('filter')
    class_filter = request.GET.get('class')

    # Compute averages per student
    averages = (
        Score.objects.filter(student__school=school)
        .values('student', 'student__first_name', 'student__last_name', 'student__school_class__id')
        .annotate(avg_score=Avg('score'))
    )

    suggestions = []
    for entry in averages:
        avg = entry['avg_score']
        student_name = f"{entry['student__first_name']} {entry['student__last_name']}"
        class_id = entry['student__school_class__id']

        if avg < 40:
            s_type, msg = 'alert', "Needs urgent attention, performance below average."
        elif 40 <= avg < 70:
            s_type, msg = 'advice', "Fair performance, could use extra support in key topics."
        else:
            s_type, msg = 'praise', "Excellent performance! Keep up the great work."

        suggestions.append({
            'student_name': student_name,
            'class_id': class_id,
            'type': s_type,
            'message': msg
        })

    # Apply filters
    if filter_type and filter_type != "all":
        suggestions = [s for s in suggestions if s['type'] == filter_type]

    if class_filter and class_filter != "all":
        suggestions = [s for s in suggestions if str(s['class_id']) == str(class_filter)]

    # 🔹 NEW: Subject performance trends for chart update
    subject_scores = Score.objects.filter(student__school=school)
    if class_filter and class_filter != "all":
        subject_scores = subject_scores.filter(student__school_class__id=class_filter)

    subject_trends = (
        subject_scores.values('subject__name')
        .annotate(average_score=Avg('score'))
        .order_by('subject__name')
    )

    trends_data = [
        {'subject': s['subject__name'], 'average_score': s['average_score']}
        for s in subject_trends
    ]

    return JsonResponse({
        'suggestions': suggestions,
        'subject_trends': trends_data  # 👈 This allows your chart to update live
    })


@login_required
def filter_dashboard(request):
    user = request.user
    school = user.school
    class_name = request.GET.get('class_name', None)

    scores = Score.objects.filter(student__school=school)
    if class_name and class_name != "All":
        scores = scores.filter(student__school_class__name=class_name)

    class_averages = list(
        scores.values('student__school_class__name')
        .annotate(average_score=Avg('score'))
        .order_by('-average_score')
    )

    top_students = list(
        scores.values('student__first_name', 'student__last_name')
        .annotate(average_score=Avg('score'))
        .order_by('-average_score')[:5]
    )

    subject_trends = list(
        scores.values('subject__name')
        .annotate(average_score=Avg('score'))
        .order_by('subject__name')
    )

    return JsonResponse({
        'class_averages': class_averages,
        'top_students': top_students,
        'subject_trends': subject_trends,
    })


def home(request):
    return render(request, 'core/home.html')

@login_required
def students(request):
    students = Student.objects.filter(school=request.user.school)
    return render(request, 'core/students.html', {'students': students})

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