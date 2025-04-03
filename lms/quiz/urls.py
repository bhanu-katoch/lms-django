from django.urls import path
from . import views

urlpatterns = [
    path('', views.quiz_list, name='quiz_list'),
    path('quiz_create/<int:course_id>', views.quiz_create, name='quiz_create'),
    path('quiz_detail/<int:quiz_id>', views.quiz_detail, name='quiz_detail'),
    path('quiz_edit/<int:quiz_id>', views.quiz_edit, name='quiz_edit'),
    path('quiz_delete/<int:quiz_id>', views.quiz_delete, name='quiz_delete'),
    path('quiz_list/<int:course_id>', views.quiz_list, name='quiz_list'),
    path('add_question/<int:quiz_id>', views.add_question, name='add_question'),
    path('delete_question/<int:question_id>', views.delete_question, name='delete_question'),
    path('edit_question/<int:question_id>', views.edit_question, name='edit_question'),
    path('<int:quiz_id>/take/', views.take_quiz, name='take_quiz'),
    path('<int:quiz_id>/result/', views.quiz_result, name='quiz_result'),
    path('<int:quiz_id>/restart/', views.restart_quiz, name='restart_quiz'),

]