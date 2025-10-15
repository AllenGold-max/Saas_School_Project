# Create your models here.
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractUser

# -------------------
# CHOICES
# -------------------
GENDER_CHOICES = [
    ('M', 'Male'),
    ('F', 'Female'),
    ('O', 'Other'),
]

TERM_CHOICES = [
    ('1', 'First Term'),
    ('2', 'Second Term'),
    ('3', 'Third Term'),
]


# -------------------
# SCHOOL MODEL
# -------------------
class School(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Schools"


# -------------------
# CUSTOM USER MODEL
# -------------------
class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='teacher')
    school = models.ForeignKey('School', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.username} ({self.role})"


# -------------------
# CLASS MODEL
# -------------------
class SchoolClass(models.Model):
    name = models.CharField(max_length=100)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='classes')
    year = models.CharField(max_length=20, blank=True)  # optional field like "2024/2025"

    class Meta:
        unique_together = ('name', 'school')
        verbose_name_plural = "Classes"

    def __str__(self):
        return f"{self.name} ({self.year}) - {self.school.name}"


# -------------------
# SUBJECT MODEL
# -------------------
class Subject(models.Model):
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=20, blank=True, help_text="Optional subject code")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='subjects', null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.school.name if self.school else 'No School'})"

    class Meta:
        verbose_name_plural = "Subjects"


# -------------------
# STUDENT MODEL
# -------------------
class Student(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    admission_number = models.CharField(max_length=50, unique=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    date_of_birth = models.DateField(null=True, blank=True)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='students')
    school_class = models.ForeignKey(SchoolClass, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name_plural = "Students"

    def __str__(self):
        return f"{self.admission_number} - {self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_average_score(self):
        scores = self.scores.all()
        if not scores:
            return None
        total = sum([s.percentage() for s in scores if s.percentage() is not None])
        return round(total / len(scores), 2)


# -------------------
# SCORE MODEL
# -------------------
class Score(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='scores')
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT, related_name='scores')
    term = models.CharField(max_length=1, choices=TERM_CHOICES)
    session = models.CharField(max_length=20, help_text="e.g. 2024/2025")
    score = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    max_score = models.DecimalField(max_digits=5, decimal_places=2, default=100)
    recorded_by = models.ForeignKey('CustomUser', on_delete=models.SET_NULL, null=True, blank=True)
    date_recorded = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['term', 'session']),
        ]
        unique_together = ('student', 'subject', 'term', 'session')
        verbose_name_plural = "Scores"

    def percentage(self):
        try:
            return (float(self.score) / float(self.max_score)) * 100
        except Exception:
            return None

    def __str__(self):
        return f"{self.student.full_name} | {self.subject.name} | {self.term} | {self.session} | {self.score}"
