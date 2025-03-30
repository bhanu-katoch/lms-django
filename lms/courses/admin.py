from django.contrib import admin
from .models import Course

# Register your models here.

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor')  # Display title and instructor
    search_fields = ('title', 'instructor__username')  # Add search functionality
    list_filter = ('instructor',)  # Filter by instructor

