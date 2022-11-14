from django.contrib import admin

from assessment.models import Assessment, ApplicationType, AssessmentSession
from questions_category.models import Question, Category
# Register your models here.

admin.site.register(Assessment)
admin.site.register(ApplicationType)
admin.site.register(AssessmentSession)
admin.site.register(Category)
admin.site.register(Question)

