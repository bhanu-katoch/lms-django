from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from courses.models import Course

all_courses = Course.objects.all()  # Fetch all courses

def home(request):
    """Publicly accessible homepage."""
    return render(request, 'lms/home.html',{"all_courses":all_courses})

@login_required
def dashboard(request):
    """Render different dashboards based on user role."""
    if request.user.role == 'student':
        enrolled_courses = request.user.enrolled_courses.all() if hasattr(request.user, 'enrolled_courses') else None
        context = {
            'all_courses': all_courses,
            'enrolled_courses': enrolled_courses
        }
        return render(request, 'lms/student_dashboard.html', context)
    elif request.user.role == 'instructor':
        taught_courses = request.user.enrolled_courses.all() if hasattr(request.user, 'enrolled_courses') else None
        context = {
            'all_courses': all_courses,
            'taught_courses': taught_courses
        }
        return render(request, 'lms/instructor_dashboard.html',context)
    elif request.user.role == 'admin':
        return render(request, 'lms/admin_dashboard.html',{'all_courses':all_courses})
    else:
        return render(request, 'lms/home.html',{'all_courses':all_courses})  # Default case
