from django.urls import path
from . import views

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('add/', views.add_course, name='add_course'),
    path('<int:course_id>/', views.course_detail, name='course_detail'),
    path('<int:course_id>/enroll/', views.enroll_course, name='enroll'),
    path("payment/<int:course_id>/", views.create_payment, name="payment"),
    path("success/", views.payment_success, name="payment_success"),
]
