from django.db import models


# Create your models here.

class Category(models.Model):
    assessment = models.ForeignKey("Assessment", on_delete=models.CASCADE)
    category_info = models.TextField()
    name = models.CharField(max_length=150)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Question(models.Model):
    TYPES = (
        ("Practice", "Practice"),
        ("Real", "Real")
    )

    DIFFICULTS = (
        ("Easy", "Easy"),
        ("Intermediate", "Intermediate"),
        ("Experience", "Experience")
    )

    test_category = models.ForeignKey(Category, on_delete=models.CASCADE)
    question_text = models.TextField()
    question_type = models.CharField(max_length=150, choices=TYPES)
    difficult = models.CharField(max_length=150, choices=DIFFICULTS)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.question_text


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=150)
    is_correct = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
from django.db import models

# Create your models here.
