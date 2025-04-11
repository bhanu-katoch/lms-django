from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import CourseForm
from django.contrib import messages
from .models import Course, Payment
from django.db.models import Q 
from django.views.decorators.csrf import csrf_exempt
import razorpay 
from django.conf import settings
from quiz.models import Quiz,QuizAttempt

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

@login_required
def edit_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    # Only the instructor should edit
    if request.user.role != "instructor":
        return redirect('course_list', course_id=course.id)

    if request.method == "POST":
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            return redirect('manage_course', course_id=course.id)
    else:
        form = CourseForm(instance=course)

    return render(request, "courses/edit_course.html", {"form": form, "course": course})

@login_required
def delete_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    if request.method == "POST":
        course.delete()
        messages.success(request, "Course deleted successfully!")
        return redirect("course_list")  # Redirect to the instructor's dashboard
    
    return render(request, "courses/course_delete.html", {"course": course})

@login_required
def manage_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    quizzes = Quiz.objects.filter(course=course)
    # assignments = Assignment.objects.filter(course=course)
    
    context = {
        'course': course,
        'quizzes': quizzes,
        # 'assignments': assignments
    }
    return render(request, 'courses/manage_course.html', context)

@login_required
def course_detail(request, course_id):
    """View to display course details and handle enrollment actions."""
    course = get_object_or_404(Course, id=course_id)
    is_enrolled = request.user in course.students.all()
    
    return render(request, 'courses/course_detail.html', {
        'course': course,
        'is_enrolled': is_enrolled
    })

from django.http import HttpResponseForbidden

@login_required
def course_content(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    authorized = course.is_free() or request.user in course.students.all()

    quizzes = Quiz.objects.filter(course=course)
    quiz_attempts = {attempt.quiz.id: attempt for attempt in QuizAttempt.objects.filter(student=request.user)}

    return render(request, "courses/course_content.html", {
        "course": course,
        "quizzes": quizzes,
        "quiz_attempts": quiz_attempts,
        "authorized": authorized,  # <-- send this to template
    })


@login_required
def enroll_course(request, course_id):
    """View to enroll a user in a course, with admin auto-enrolled and instructors restricted."""
    course = get_object_or_404(Course, id=course_id)
    
    # Admins get free access automatically
    if request.user.is_superuser:
        course.students.add(request.user)
        messages.success(request, "You have been automatically enrolled as an admin.")
        return redirect('course_detail', course_id=course.id)
    
    # Instructors cannot enroll in courses
    if request.user.role == 'instructor':
        messages.error(request, "Instructors cannot enroll in courses.")
        return redirect('course_detail', course_id=course.id)

    # Check if the user is already enrolled
    if request.user in course.students.all():
        messages.info(request, "You are already enrolled in this course.")
        return redirect('course_detail', course_id=course.id)

    # If the course is free, enroll directly
    if course.is_free():
        course.students.add(request.user)
        messages.success(request, "You have successfully enrolled in the course!")
        return redirect('course_detail', course_id=course.id)

    # If the course is paid, redirect to payment
    return redirect('payment', course_id=course.id)

# @login_required
# def payment_page(request, course_id):
#     """View to handle payments for paid courses"""
#     course = get_object_or_404(Course, id=course_id)

#     # If the user is already enrolled, redirect to course
#     if request.user in course.students.all():
#         messages.info(request, "You are already enrolled in this course.")
#         return redirect('course_detail', course_id=course.id)

#     # Fake Payment Processing (Replace with Payment Gateway Integration)
#     if request.method == "POST":
#         course.students.add(request.user)
#         messages.success(request, "Payment successful! You are now enrolled in the course.")
#         return redirect('course_detail', course_id=course.id)

#     return render(request, 'courses/payment_page.html', {'course': course})

# Initialize Razorpay Client
from django.http import JsonResponse

def create_payment(request, course_id):
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    course = Course.objects.get(id=course_id)

    # Create order in Razorpay
    order_data = {
        "amount": int(course.price)*100,# Convert to paise
        "currency": settings.RAZORPAY_CURRENCY,
        "payment_capture": "1"  # Auto-capture payment
    }
    order = client.order.create(data=order_data)

    # Save payment record in the database
    Payment.objects.create(
        user=request.user,
        course=course,
        amount=course.price,
        status="Pending",
        order_id=order["id"]
    )

    return render(request, "courses/payment_page.html", {
        "key_id": settings.RAZORPAY_KEY_ID,
        "order_id": order["id"],
        "amount": int(course.price),
        "currency": settings.RAZORPAY_CURRENCY,
        "course": course,
    })

import logging
logger = logging.getLogger(__name__)  # Initialize the logger
import json
@csrf_exempt
def payment_success(request):
    logger.info(f"Received request with method: {request.method}")  # Log request method
    if request.method == "GET":
        return JsonResponse({"error": "Please send a POST request"}, status=400)

    if request.method == "POST":
        try:
            # Handle JSON data if sent in JSON format
            if request.content_type == "application/json":
                data = json.loads(request.body)
            else:
                data = request.POST

            logger.info(f"Received data: {data}")  # Log request data

            order_id = data.get("razorpay_order_id")
            payment_id = data.get("razorpay_payment_id")
            signature = data.get("razorpay_signature")

            # Log extracted values
            logger.info(f"Order ID: {order_id}, Payment ID: {payment_id}, Signature: {signature}")

            if not order_id or not payment_id or not signature:
                return JsonResponse({"error": "Missing required fields"}, status=400)

            # Fetch payment record
            payment = Payment.objects.get(order_id=order_id)

            # Verify payment signature
            params_dict = {
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }

            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            client.utility.verify_payment_signature(params_dict)


            # Update payment record
            payment.payment_id = payment_id
            payment.status = "Success"
            payment.save()
            #update student record
            user = payment.user  # Assuming payment model has a foreign key to User
            course = payment.course
            course.students.add(user)

            logger.info("Payment verified successfully!")  # Log success

            return JsonResponse({"success": True})

        except Payment.DoesNotExist:
            logger.error("Payment record not found in database")  # Log error
            return JsonResponse({"error": "Payment record not found in database"}, status=400)

        except razorpay.errors.SignatureVerificationError:
            logger.error("Signature verification failed")  # Log error
            return JsonResponse({"error": "Signature verification failed"}, status=400)

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")  # Log any other exception
            return JsonResponse({"error": str(e)}, status=400)

    logger.warning("Invalid request method")  # Log invalid request method
    return JsonResponse({"error": "Invalid request method"}, status=400)
