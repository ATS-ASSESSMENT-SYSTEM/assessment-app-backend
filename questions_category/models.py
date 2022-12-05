import datetime

from django.db import models

# Create your models here.
from django.utils import timezone


# from assessment.models import Assessment

class ActiveManager(models.Manager):
    def get_queryset(self):
        return super(ActiveManager, self).get_queryset().filter(is_delete=False)


class DeleteManager(models.Manager):
    def get_queryset(self):
        return super(DeleteManager, self).get_queryset().filter(is_delete=True)


class Category(models.Model):
    category_info = models.TextField()
    name = models.CharField(max_length=150)
    test_duration = models.TimeField(default=datetime.time(00, 10, 00))
    num_of_questions = models.IntegerField(default=10)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    is_delete = models.BooleanField(default=False)

    objects = models.Manager()
    active_objects = ActiveManager()
    deleted_objects = DeleteManager()

    def __str__(self):
        return self.name

    def category_question(self):
        q = Question.objects.filter(test_category=self.id)
        return q

    class Meta:
        ordering = ('-created_date',)

    def questions(self):
        return self.question_set.filter(is_delete=False)

    def num_of_questions_in_category(self):
        return self.question_set.filter(is_delete=False).count()


class Question(models.Model):
    QUESTION_CATEGORIES = (
        ("Practice", "Practice"),
        ("Real", "Real")
    )

    TYPES = (
        ("Multi-choice", "Multi-choice"),
        ("Open-ended", "Open-ended"),
        ("Multi-response", "Multi-response")
    )

    test_category = models.ForeignKey(Category, on_delete=models.CASCADE)
    question_text = models.TextField()
    question_type = models.CharField(
        max_length=150, default='Multi-choice', choices=TYPES)
    question_category = models.CharField(
        max_length=150, choices=QUESTION_CATEGORIES, default='Real')
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    is_delete = models.BooleanField(default=False)

    objects = models.Manager()
    active_objects = ActiveManager()
    deleted_objects = DeleteManager()

    def __str__(self):
        return self.question_text

    class Meta:
        ordering = ('-created_date',)

    def SessionAnswer(self):
        return self.SessionAnswer_set.all()

    def choices(self):
        return self.choice_set.filter(is_delete=False)

    def open_ended_answer_text(self):
        return self.answer.filter(is_delete=False)


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=255)
    is_correct = models.BooleanField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    is_delete = models.BooleanField(default=False)

    objects = models.Manager()
    active_objects = ActiveManager()
    deleted_objects = DeleteManager()

    def __str__(self):
        return self.choice_text


class OpenEndedAnswer(models.Model):
    question = models.ForeignKey(
        Question, related_name="answer", on_delete=models.CASCADE)
    candidate = models.CharField(max_length=150, null=True, blank=True)
    answer_text = models.TextField()
    is_correct = models.BooleanField(default=False)
    is_marked = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, null=True, blank=True)
    is_delete = models.BooleanField(default=False)

    objects = models.Manager()
    active_objects = ActiveManager()
    deleted_objects = DeleteManager()
