from django.contrib import admin
from . import models


admin.site.site_header = "SRT Academy Administration"
admin.site.site_title = "SRT Academy Admin"
admin.site.index_title = "Welcome to SRT Academy Administration"


@admin.register(models.Profile)
class ProfileAdmin(admin.ModelAdmin):
    pass

@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    pass

@admin.register(models.Course)
class CourseAdmin(admin.ModelAdmin):
    pass

@admin.register(models.Lesson)
class LessonAdmin(admin.ModelAdmin):
    pass

@admin.register(models.EnrolledCourse)
class EnrolledCourseAdmin(admin.ModelAdmin):
    pass

@admin.register(models.LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    pass

@admin.register(models.Rating)
class RatingAdmin(admin.ModelAdmin):
    pass

@admin.register(models.SavedCourse)
class SavedCoursAdmin(admin.ModelAdmin):
    pass
