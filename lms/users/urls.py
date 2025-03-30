from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_user, name='home_user'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.register, name='register'),
]
