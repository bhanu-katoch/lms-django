from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from courses.models import Course
from django.db.models import Q

def home(request):
    """Home page with course listing and search functionality."""
    query = request.GET.get('q', '').strip()  # Get search query from navbar
    all_courses = Course.objects.all()  # Fetch all courses

    if query:  
        all_courses = all_courses.filter(
            Q(title__icontains=query) | Q(description__icontains=query)  # Search in title and description
        )

    return render(request, 'lms/home.html', {
        'all_courses': all_courses,
        'query': query  # Pass search query back to template
    })

@login_required
def dashboard(request):
    """Render different dashboards based on user role, with search functionality."""
    query = request.GET.get('q', '').strip()  # Get search query from navbar
    all_courses = Course.objects.all()  # Get all courses
    enrolled_courses = None
    taught_courses = None

    # Apply search filter
    if query:
        all_courses = all_courses.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    # Handle user roles
    if request.user.role == 'student':
        enrolled_courses = request.user.enrolled_courses.all()
        if query:
            enrolled_courses = enrolled_courses.filter(
                Q(title__icontains=query) | Q(description__icontains=query)
            )
        return render(request, 'lms/student_dashboard.html', {
            'all_courses': all_courses,
            'enrolled_courses': enrolled_courses,
            'query': query
        })

    elif request.user.role == 'instructor':
        taught_courses = request.user.courses_taught.all()  # Corrected from `enrolled_courses`
        if query:
            taught_courses = taught_courses.filter(
                Q(title__icontains=query) | Q(description__icontains=query)
            )
        return render(request, 'lms/instructor_dashboard.html', {
            'all_courses': all_courses,
            'taught_courses': taught_courses,
            'query': query
        })

    elif request.user.role == 'admin':
        return render(request, 'lms/admin_dashboard.html', {
            'all_courses': all_courses,
            'query': query
        })

    return render(request, 'lms/home.html', {'all_courses': all_courses, 'query': query})  # Default case


