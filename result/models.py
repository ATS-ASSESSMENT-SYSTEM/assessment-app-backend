import json

from django.core import serializers
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.db import models
from django.db.models import Sum

from assessment.models import Assessment, AssessmentSession
from questions_category.models import Category, Question, Choice, OpenEndedAnswer


# from api.serializers import AssessmentImageSerializer

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
    applicant_info = models.JSONField(default=call_json(type_='dict'), null=True, blank=True)

    def __str__(self) -> str:
        return f'{self.candidate} result for {self.assessment}'

    def category_info(self):
        return self.category_result_set.all()

    @property
    def result_status(self) -> str:
        category_check = Category_Result.objects.filter(result_id=self.id, has_open_ended=True)
        if category_check.exists():
            print("check=>", category_check.values_list('pk'))
            opa_check = OpenEndedAnswer.object.filter(category_pk__in=category_check.values_list('pk', flat=True),
                                                     )
            print("check_2 =>", opa_check)
            if opa_check.exists():
                return 'Inconclusive'
        assessment = Assessment.objects.get(pk=self.assessment.pk)
        assessment_benchmark = assessment.benchmark
        print("info", assessment_benchmark, self.result_total)

        mark_obtained = self.result_total['score__sum']

        if assessment_benchmark > mark_obtained:
            return 'Failed'
        if assessment_benchmark < mark_obtained:
            return 'Passed'

    @property
    def result_total(self) -> int:
        q = Category_Result.objects.filter(result_id=self.id). \
            aggregate(Sum('score'))
        return q

    @property
    def duration(self):
        print(self.candidate, self.id)
        sessions = AssessmentSession.objects.filter(assessment_id=self.assessment.pk, candidate_id=self.candidate) \
            .order_by('date_created')
        print(sessions.first())
        return {
            "time_started": sessions.first().date_created,
            "time_ended"
            : sessions.last().date_created
        }

    @property
    def percentage_total(self):
        # mark_obtainable = Category_Result.objects.filter(result_id=self.assessment)
        print('inside percentage', self.assessment.number_of_question)
        total_questions = self.assessment.number_of_question
        print("total_question", self.id, total_questions)
        return ''

    @property
    def images(self):
        q = AssessmentImages.objects.filter(assessment=self.assessment, candidate=self.candidate)
        if q.exists():
            return json.loads(q)
        return []

    @property
    def feedback(self):
        try:
            fb = AssessmentFeedback.objects.get(applicant_info__applicantId=self.candidate,
                                                assessment=self.assessment)

            return fb.feedback
        except AssessmentFeedback.DoesNotExist:
            return {}

    class Meta:
        unique_together = ('assessment', 'candidate')


class Category_Result(models.Model):
    result = models.ForeignKey(Result, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    score = models.IntegerField()
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    has_open_ended = models.BooleanField(default=False)
    status = models.CharField(max_length=100, default="TAKEN")

    def __str__(self) -> str:
        return f'{self.result} result for {self.category}'


class Session_Answer(models.Model):
    TYPES = (
        ("Multi-choice", "Multi-choice"),
        ("Open-ended", "Open-ended"),
        ("Multi-response", "Multi-response")
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
    mr_answers_id = models.JSONField(default=call_json(type_='list'), null=True, blank=True)

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
