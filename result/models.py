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
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    candidate = models.CharField(max_length=150)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    applicant_info = models.JSONField(
        default=call_json(type_='dict'), null=True, blank=True)

    def __str__(self) -> str:
        return f'{self.candidate} result for {self.assessment}'

    def category_info(self):
        return self.CategoryResult_set.all()

    @property
    def result_status(self) -> str:
        category_check = CategoryResult.objects.filter(
            result_id=self.id, has_open_ended=True)
        if category_check.exists():
            opa_check = OpenEndedAnswer.object.filter(category__in=category_check.values_list('pk')
                                                      ,is_marked=False)
            if opa_check.exists():
                return 'Inconclusive'

        assessment = Assessment.objects.get(pk=self.assessment.pk)
        assessment_benchmark = assessment.benchmark
        print(assessment_benchmark, self.result_total)
        # if assessment_benchmark > self.result_total:
        #     return 'Failed'
        #
        # if assessment_benchmark < self.result_total:
        #     return 'Passed'

        return 'Still Processing'

    @property
    def result_total(self) -> int:
        # fetch all categories for the candidate
        candidate_category = CategoryResult.objects.filter(result_id=self.id)
        # fetch all category ofr the assessment
        assessment_category = self.assessment.category.all()

        q = CategoryResult.objects.filter(
            result_id=self.id).aggregate(Sum('score'))

        if candidate_category.count() == assessment_category.count():
            return q['score__sum']

        unfinished_category = assessment_category.exclude(
            pk__in=candidate_category.values_list('category'))

        unfinished_category_answer = SessionAnswer.objects.filter(category__in=unfinished_category,
                                                                  assessment=self.assessment,
                                                                  candidate=self.candidate,
                                                                  is_correct=True
                                                                  )
        available_category = unfinished_category.filter(
            pk__in=unfinished_category_answer.values_list('category'))
        print("checks=>", unfinished_category_answer.values_list('category'),
              unfinished_category.values_list('id'), available_category)

        check_category = CategoryResult.objects.filter(
            result_id=self.id,
            category__in=unfinished_category_answer.values_list('category')
        )
        if not check_category.exists():
            # create un_finished_category
            for category in available_category:
                correct_score = SessionAnswer.objects.filter(Q(question_type='Multi-choice') |
                                                             Q(question_type='Multi-response'),
                                                             is_correct=True,
                                                             candidate=self.candidate,
                                                             assessment=self.assessment,
                                                             category=category
                                                             )

                has_open_ended_answer = OpenEndedAnswer.objects.filter(candidate=self.candidate,
                                                                       category=category)

                has_open_ended = bool(has_open_ended_answer.count())

                get_or_create = CategoryResult(
                    result_id=self.id,
                    category=category,
                    score=correct_score.count(),
                    has_open_ended=has_open_ended,
                    status='STARTED'
                )
                get_or_create.save()

        return q['score__sum'] + unfinished_category_answer.count()

    @property
    def duration(self):
        sessions = AssessmentSession.objects.filter(assessment_id=self.assessment.pk, candidate_id=self.candidate) \
            .order_by('date_created')
        print(sessions.first())
        # return  sessions.first().date_created
        return {
            "time_started": sessions.first().date_created,
            "time_ended": sessions.last().date_created
        }

    @property
    def percentage_total(self):
        # mark_obtainable = CategoryResult.objects.filter(result_id=self.assessment)
        total_questions = self.assessment.number_of_questions_in_assessment
        total_mark_obtained = self.result_total

        return (total_mark_obtained / total_questions) * 100

    @property
    def images(self):
        q = AssessmentImages.objects.filter(
            assessment=self.assessment, candidate=self.candidate)
        if q.exists():
            return json.loads(q)
        return []

    class Meta:
        unique_together = ('assessment', 'candidate')


class CategoryResult(models.Model):
    STATUS = (
        ('STARTED', 'STARTED'),
        ('FINISHED', 'FINISHED')
    )
    result = models.ForeignKey(Result, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    score = models.IntegerField()
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    has_open_ended = models.BooleanField(default=False)
    status = models.CharField(max_length=100, default="TAKEN")

    def __str__(self) -> str:
        return f'{self.result} result for {self.category}'


class SessionAnswer(models.Model):
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
    question_type = models.CharField(
        max_length=150, default='Multi-choice', choices=TYPES)
    choice = models.ForeignKey(
        Choice, on_delete=models.CASCADE, null=True, blank=True)
    mr_answers_id = models.JSONField(
        default=call_json(type_='list'), null=True, blank=True)

    def __str__(self):
        return f'Answer for {self.question}'


class AssessmentImages(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    candidate = models.CharField(max_length=50)
    image = models.ImageField(null=True, blank=True,
                              upload_to='session_images')
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
    media_type = models.CharField(
        max_length=50, choices=TYPES, default="Image")
    candidate = models.CharField(max_length=50)
    media = models.FileField(null=True, blank=True,
                             upload_to="candidate_media")
    uploaded_at = models.DateTimeField(auto_now_add=True)


class AssessmentFeedback(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    applicant_info = models.JSONField(
        default=call_json(type_='dict'), null=True, blank=True)
    feedback = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    reaction = models.CharField(
        null=True, blank=True, max_length=50, choices=REACTION, default='Ok')
