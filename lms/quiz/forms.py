from django import forms
from .models import Quiz, Question, Option, QuizResponse
from django.forms import inlineformset_factory

class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'description']  # Remove 'course' from fields

    def __init__(self, *args, **kwargs):
        course = kwargs.pop('course', None)  # Get course from kwargs
        super().__init__(*args, **kwargs)
        self.course = course  # Store course instance

    def save(self, commit=True):
        quiz = super().save(commit=False)
        if self.course:
            quiz.course = self.course  # Assign course dynamically
        if commit:
            quiz.save()
        return quiz

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text']

class OptionForm(forms.ModelForm):
    class Meta:
        model = Option
        fields = ['text', 'is_correct']

OptionFormSet = inlineformset_factory(
    Question, 
    Option, 
    form=OptionForm, 
    extra=4,  # Always show up to 4 blank options in add mode
    max_num=4,  # Prevents more than 4 options from being added
    can_delete=True  # Allow deleting options
)

class QuizResponseForm(forms.ModelForm):
    class Meta:
        model = QuizResponse
        fields = ['selected_option']
    
    def __init__(self, *args, **kwargs):
        question = kwargs.pop('question', None)
        super().__init__(*args, **kwargs)
        if question:
            self.fields['selected_option'].queryset = question.options.all()
            self.fields['selected_option'].widget = forms.RadioSelect()
