from django.contrib import admin
from .models import Quiz, Question, Option, QuizAttempt, QuizResponse

class OptionInline(admin.TabularInline):
    """Inline options for questions in Django Admin."""
    model = Option
    extra = 2  # Show two empty option fields by default

class QuestionInline(admin.TabularInline):
    """Inline questions for quizzes in Django Admin."""
    model = Question
    extra = 1  # Show one empty question field by default

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'total_questions')
    list_filter = ('course',)
    search_fields = ('title',)
    inlines = [QuestionInline]  # Allow adding questions inline in Quiz Admin

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'quiz')
    search_fields = ('text',)
    list_filter = ('quiz',)
    inlines = [OptionInline]  # Allow adding options inline in Question Admin

@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ('text', 'question', 'is_correct')
    list_filter = ('is_correct',)
    search_fields = ('text',)

@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('student', 'quiz', 'score', 'completed', 'attempt_date')
    list_filter = ('completed', 'attempt_date')
    search_fields = ('student__username', 'quiz__title')

@admin.register(QuizResponse)
class QuizResponseAdmin(admin.ModelAdmin):
    list_display = ('attempt', 'question', 'selected_option', 'is_correct')
    list_filter = ('attempt',)
    search_fields = ('question__text',)

    def is_correct(self, obj):
        return obj.is_correct()
    is_correct.boolean = True
    is_correct.short_description = "Correct Answer"

