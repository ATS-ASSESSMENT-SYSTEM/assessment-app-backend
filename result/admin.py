from django.contrib import admin
from result.models import Result, CategoryResult, \
    SessionAnswer, AssessmentImages, AssessmentMedia, AssessmentFeedback
# Register your models here.

admin.site.register(Result)
admin.site.register(CategoryResult)
admin.site.register(SessionAnswer)
admin.site.register(AssessmentImages)
admin.site.register(AssessmentMedia)
admin.site.register(AssessmentFeedback)
