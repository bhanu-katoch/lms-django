from django.urls import path
from . import views

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('add/', views.add_course, name='add_course'),
    path('manage/<int:course_id>/', views.manage_course, name='manage_course'),
    path('edit/<int:course_id>/', views.edit_course, name='edit_course'),
    path('delete/<int:course_id>/', views.delete_course, name='delete_course'),
    path('<int:course_id>/', views.course_detail, name='course_detail'),
    path('<int:course_id>/content', views.course_content, name='course_content'),
    path('<int:course_id>/enroll/', views.enroll_course, name='enroll'),
    path("payment/<int:course_id>/", views.create_payment, name="payment"),
    path("success/", views.payment_success, name="payment_success"),
]
