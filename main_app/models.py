from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import timedelta
from django.utils import timezone


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to="user_avatars", blank=True, null=True)
    bio = models.TextField(max_length=160, blank=True)
    is_instructor = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

class Category(models.Model):
    name = models.CharField(max_length=25, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"


class Course(models.Model):
    instructor = models.ForeignKey(Profile, on_delete=models.PROTECT, related_name="courses")
    categories = models.ManyToManyField(Category,  blank=True, related_name="courses")

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(max_length=510, blank=True)
    cover_image = models.ImageField(upload_to="course_images")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)

    @property
    def can_edit_lessons(self):
        if self.is_published:
            return False
        return timezone.now() < self.created_at + timedelta(days=7)

    def __str__(self):
        return self.title

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(
                        is_published=True,
                        published_at__isnull=False
                    )
                    |
                    models.Q(
                        is_published=False,
                        published_at__isnull=True
                    )
                ),
                name="valid_course_publication_state"
            )
        ]


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=160)
    order = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    video_url = models.URLField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["order"]
        constraints = [
            models.UniqueConstraint(
                fields=["course", "order"],
                name="unique_order_per_course"
            )
        ]

class EnrolledCourse(models.Model):
    student = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="enrolled_courses")
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name="enrollments")
    enrolled_at = models.DateTimeField(auto_now_add=True)
    last_accessed_at = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)

    class Meta:
        ordering = ['-last_accessed_at']
        constraints = [
            models.UniqueConstraint(
                fields=["student", "course"],
                name="unique_enrolled_course_per_student",
            )
        ]

class LessonProgress(models.Model):
    student = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="lesson_progress")
    lesson = models.ForeignKey(Lesson, on_delete=models.PROTECT, related_name="progress")

    started_at = models.DateTimeField(auto_now_add=True)
    last_position = models.PositiveIntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Lesson Progress"
        verbose_name_plural = "Lesson Progress"
        constraints = [
            models.UniqueConstraint(
                fields=["student", "lesson"],
                name="uniquelesson_progress_per_student"
            )
        ]

class Rating(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="ratings")
    student = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="ratings_given")
    value = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(max_length=160, blank=True)
    rated_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "course"],
                name="unique_course_rating_per_student"
            )
        ]

class SavedCourse(models.Model):
    student = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="saved_courses")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="saves")
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "course"],
                name="unique_course_save_per_student"
            )
        ]