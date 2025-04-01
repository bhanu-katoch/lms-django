from django.contrib import admin
from .models import Course,Payment

# Register your models here.

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor')  # Display title and instructor
    search_fields = ('title', 'instructor__username')  # Add search functionality
    list_filter = ('instructor',)  # Filter by instructor

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'amount', 'status', 'payment_id', 'order_id', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'course__title', 'payment_id', 'order_id')
    ordering = ('-created_at',)