import datetime

from django.db import models

# Create your models here.
from django.utils import timezone


# from assessment.models import Assessment


class Category(models.Model):
    assessment = models.ManyToManyField('assessment.Assessment', limit_choices_to={'is_delete': False})
    category_info = models.TextField()
    name = models.CharField(max_length=150)
    test_duration = models.TimeField(default=datetime.time(00, 10, 00))
    num_of_questions = models.IntegerField(default=10)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('-created_date',)


class Question(models.Model):
    QUESTION_CATEGORIES = (
        ("Practice", "Practice"),
        ("Real", "Real")
    )

    TYPES = (
        ("Multi-choice", "Multi-choice"),
        ("Open-ended", "Open-ended")
    )

    test_category = models.ForeignKey(Category, on_delete=models.CASCADE)
    question_text = models.TextField()
    question_type = models.CharField(max_length=150, default='Multi-choice', choices=TYPES)
    question_categories = models.CharField(max_length=150, choices=QUESTION_CATEGORIES, default='Real')
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    question_hint = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.question_text

    class Meta:
        ordering = ('-created_date',)
        
    def session_answer(self):
        return self.session_answer_set.all()

    def session_answer(self):
        return self.session_answer_set.all()


class Choice(models.Model):
    question = models.ForeignKey(Question, related_name="choices", on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.choice_text

    def __str__(self):
        return self.choice_text


class OpenEndedAnswer(models.Model):
    question = models.ForeignKey(Question, related_name="answer", on_delete=models.CASCADE)
    candidate = models.CharField(max_length=150, null=True, blank=True)
    answer_text = models.TextField()
    is_correct = models.BooleanField(default=False)
    is_marked = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
