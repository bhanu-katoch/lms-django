from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from .models import Course
from .forms import CourseForm

# Create your views here.

def course_list(request):
    """Show courses based on user role, but allow guests to see all courses"""
    all_courses = Course.objects.all()  # Everyone can see all courses
    enrolled_courses = None
    taught_courses = None

    if request.user.is_authenticated:  # If user is logged in
        if request.user.role == 'student':
            enrolled_courses = request.user.enrolled_courses.all()  # Student's enrolled courses
        elif request.user.role == 'instructor':
            taught_courses = request.user.courses_taught.all()  # Instructor's own courses

    return render(request, 'courses/course_list.html', {
        'all_courses': all_courses,
        'enrolled_courses': enrolled_courses,
        'taught_courses': taught_courses
    })

@login_required
def add_course(request):
    if request.user.role != 'instructor':  # Only instructors can add courses
        return redirect('course_list')

    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = request.user  # Set instructor to logged-in user
            course.save()
            return redirect('course_list')

    else:
        form = CourseForm()

    return render(request, 'courses/add_course.html', {'form': form})