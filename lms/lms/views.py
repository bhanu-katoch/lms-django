from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def home(request):
    """Publicly accessible homepage."""
    return render(request, 'lms/home.html')

@login_required
def dashboard(request):
    """Render different dashboards based on user role."""
    if request.user.role == 'student':
        return render(request, 'lms/student_dashboard.html')
    elif request.user.role == 'instructor':
        return render(request, 'lms/instructor_dashboard.html')
    elif request.user.role == 'admin':
        return render(request, 'lms/admin_dashboard.html')
    else:
        return render(request, 'lms/home.html')  # Default case
