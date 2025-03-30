from django.urls import path
from .views import course_list, add_course

urlpatterns = [
    path('', course_list, name='course_list'),
    path('add/', add_course, name='add_course'),
]
