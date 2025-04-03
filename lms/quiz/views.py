# CRUD Views for Quizzes, Questions, and Options
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .forms import QuizForm, QuestionForm, OptionForm,OptionFormSet
from .models import Quiz,Question,Option
from courses.models import Course

def quiz_list(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    quizzes = Quiz.objects.filter(course=course)
    return render(request, "quiz_list.html", {"quizzes": quizzes, "course": course})

@login_required
def quiz_detail(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    return render(request, 'quiz_detail.html', {'quiz': quiz})

@login_required
def quiz_create(request, course_id):
    course = get_object_or_404(Course, id=course_id)  # Get course by ID

    if request.method == "POST":
        form = QuizForm(request.POST, course=course)  # Pass course to form
        if form.is_valid():
            form.save()
            return redirect('manage_course',course_id)  # Redirect to quiz list
    else:
        form = QuizForm(course=course)

    return render(request, 'quiz_create.html', {'form': form, 'course': course})

@login_required
def quiz_edit(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if request.method == "POST":
        form = QuizForm(request.POST, instance=quiz)
        if form.is_valid():
            form.save()
            return redirect('manage_course',quiz.course.id)
    else:
        form = QuizForm(instance=quiz)
    return render(request, 'quiz_edit.html', {'form': form})

@login_required
def quiz_delete(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if request.method == "POST":
        quiz.delete()
        return redirect('manage_course',quiz.course.id)
    return render(request, 'quiz_delete.html', {'quiz': quiz})

@login_required
def add_question(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    if request.method == "POST":
        question_form = QuestionForm(request.POST)
        option_formset = OptionFormSet(request.POST)

        if question_form.is_valid() and option_formset.is_valid():
            question = question_form.save(commit=False)
            question.quiz = quiz  # Associate question with the quiz
            question.save()

            options = option_formset.save(commit=False)
            for option in options:
                option.question = question  # Link options to the newly created question
                option.save()
            quiz.update_total_questions()
            return redirect('quiz_detail', quiz.id)  # Redirect back to quiz detail page
    else:
        question_form = QuestionForm()
        option_formset = OptionFormSet()

    return render(request, "add_question.html", {
        "question_form": question_form,
        "option_formset": option_formset,
        "quiz": quiz
    })
from django.shortcuts import render, get_object_or_404, redirect
from .models import Question
from .forms import QuestionForm, OptionFormSet

def edit_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    quiz = question.quiz

    if request.method == "POST":
        question_form = QuestionForm(request.POST, instance=question)
        option_formset = OptionFormSet(request.POST, instance=question)

        if question_form.is_valid() and option_formset.is_valid():
            question_form.save()
            option_formset.save()
            return redirect('quiz_detail', quiz.id)
    else:
        question_form = QuestionForm(instance=question)
        option_formset = OptionFormSet(instance=question)

    return render(request, "edit_question.html", {
        "question_form": question_form,
        "option_formset": option_formset,
        "quiz": quiz,
        "question": question
    })

@login_required
def delete_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    quiz = question.quiz  # Get the related quiz

    if request.method == "POST":
        question.delete()
        quiz.update_total_questions()
        return redirect('quiz_detail', quiz.id)  # Redirect to quiz detail page after deletion

    return render(request, "delete_question.html", {"question": question, "quiz": quiz})

from .models import Quiz, Question, Option, QuizAttempt, QuizResponse
from .forms import QuizResponseForm

@login_required
def take_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    attempt, created = QuizAttempt.objects.get_or_create(student=request.user, quiz=quiz, completed=False)

    if request.method == "POST":
        for question in quiz.questions.all():
            selected_option_id = request.POST.get(f'question_{question.id}')
            if selected_option_id:
                selected_option = Option.objects.get(id=selected_option_id)
                QuizResponse.objects.update_or_create(
                    attempt=attempt, question=question, defaults={"selected_option": selected_option}
                )

        # Calculate score
        score = sum(1 for response in attempt.responses.all() if response.is_correct())
        attempt.score = score
        attempt.completed = True
        attempt.save()
        return redirect("quiz_result", quiz_id=quiz.id)

    return render(request, "take_quiz.html", {"quiz": quiz, "attempt": attempt})

@login_required
def quiz_result(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    attempt = get_object_or_404(QuizAttempt, student=request.user, quiz=quiz, completed=True)
    
    total_questions = quiz.questions.count()
    score = attempt.score
    percentage = (score / total_questions) * 100 if total_questions else 0

    return render(request, "quiz_result.html", {"quiz": quiz, "score": score, "percentage": percentage})

@login_required
def restart_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    QuizAttempt.objects.filter(student=request.user, quiz=quiz).delete()  # Delete previous attempts
    return redirect("take_quiz", quiz_id=quiz.id)  # Redirect to a fresh quiz attempt
