from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from .forms import CourseForm
from .models import Course
from django.db.models import Q  

def course_list(request):
    """Show courses based on user role, with improved search functionality"""
    
    query = request.GET.get('q', '').strip()  # Get and clean the search query
    all_courses = Course.objects.all()
    enrolled_courses = None
    taught_courses = None

    if query:  # Apply search filter (title OR description)
        all_courses = all_courses.filter(Q(title__icontains=query) | Q(description__icontains=query))

    if request.user.is_authenticated:  # If user is logged in
        if request.user.role == 'student':
            enrolled_courses = request.user.enrolled_courses.all()
            if query:
                enrolled_courses = enrolled_courses.filter(Q(title__icontains=query) | Q(description__icontains=query))

        elif request.user.role == 'instructor':
            taught_courses = request.user.courses_taught.all()
            if query:
                taught_courses = taught_courses.filter(Q(title__icontains=query) | Q(description__icontains=query))

    return render(request, 'courses/course_list.html', {
        'all_courses': all_courses,
        'enrolled_courses': enrolled_courses,
        'taught_courses': taught_courses,
        'query': query  # Pass query back to template
    })

@login_required
def add_course(request):
    if request.user.role != 'instructor':  # Only instructors can add courses
        return redirect('course_list')

    if request.method == 'POST':
        form = CourseForm(request.POST,request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = request.user  # Set instructor to logged-in user
            course.save()
            return redirect('course_list')

    else:
        form = CourseForm()

    return render(request, 'courses/add_course.html', {'form': form})