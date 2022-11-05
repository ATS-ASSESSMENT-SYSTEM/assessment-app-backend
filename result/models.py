from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.db import models

from assessment.models import Assessment
from questions_category.models import Category


class Result(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    candidate = models.CharField(max_length=50)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f'{self.candidate} result for {self.assessment}'

    class Meta:
        unique_together = ('assessment', 'candidate')


class Category_Result(models.Model):
    result = models.ForeignKey(Result, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    score = models.IntegerField()
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f'{self.result} result for {self.category}'
