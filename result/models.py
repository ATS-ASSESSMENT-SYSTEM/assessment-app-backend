from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.db import models
from django.db.models import Sum

from assessment.models import Assessment, AssessmentSession
from questions_category.models import Category, Question, Choice, OpenEndedAnswer


def call_json(type_: str):
    if type_ == 'dict':
        return dict
    return list


class Result(models.Model):
    STATUS = (
        ("Passed", "PASSED"),
        ("Failed", "FAILED"),
        ('Inconclusive', "INCONCLUSIVE")
    )
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    candidate = models.CharField(max_length=150)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    status = models.CharField(max_length=150, choices=STATUS, default='Inconclusive')
    total = models.IntegerField(default=0)
    applicant_info = models.JSONField(default=call_json(type_='dict'), null=True, blank=True)

    def __str__(self) -> str:
        return f'{self.candidate} result for {self.assessment}'

    def category_info(self):
        return self.category_result_set.all()

    @property
    def result_status(self) -> str:
        category_check = Category_Result.objects.filter(result_id=self.id)
        if category_check.exclude(has_open_ended=True).exists():
            opa_check = OpenEndedAnswer.object.filter(category__in=category_check)
            if opa_check.exclude(is_marked=False):
                return 'Inconclusive'

    @property
    def result_total(self)-> int:
        return Category_Result.objects.filter(result_id=self.id).\
            aggregate(Sum('score'))


    class Meta:
        unique_together = ('assessment', 'candidate')


class Category_Result(models.Model):
    STATUS = (
        ("STARTED", "STARTED"),
        ("NOT-STARTED", "NOT-STARTED"),
        ("TAKEN", "TAKEN"),

    )

    result = models.ForeignKey(Result, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    score = models.IntegerField()
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    has_open_ended = models.BooleanField(default=False)
    status = models.CharField(max_length=100, choices=STATUS, default="NOT-STARTED")

    def __str__(self) -> str:
        return f'{self.result} result for {self.category}'


class Session_Answer(models.Model):
    TYPES = (
        ("Multi-choice", "Multi-choice"),
        ("Open-ended", "Open-ended")
    )
    candidate = models.CharField(max_length=150)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    is_correct = models.BooleanField(default=False)
    session = models.ForeignKey(AssessmentSession, on_delete=models.CASCADE)
    time_remaining = models.CharField(max_length=50)
    question_type = models.CharField(max_length=150, default='Multi-choice', choices=TYPES)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f'Answer for {self.question}'


class AssessmentImages(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    candidate = models.CharField(max_length=50)
    image = models.ImageField(null=True, blank=True, upload_to='session_images')
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_date"]


class AssessmentMedia(models.Model):
    TYPES = (
        ("Sound", "SOUND"),
        ("Video", "VIDEO"),
        ("Image", "IMAGE")
    )
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    media_type = models.CharField(max_length=50, choices=TYPES, default="Image")
    candidate = models.CharField(max_length=50)
    media = models.FileField(null=True, blank=True, upload_to="candidate_media")
    uploaded_at = models.DateTimeField(auto_now_add=True)


class AssessmentFeedback(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    applicant_info = models.JSONField(default=call_json(type_='dict'), null=True, blank=True)
    feedback = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
