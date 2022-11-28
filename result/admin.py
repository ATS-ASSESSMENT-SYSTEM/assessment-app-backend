from django.contrib import admin
from result.models import Result, Category_Result, \
    Session_Answer, AssessmentImages ,AssessmentMedia, AssessmentFeedback
# Register your models here.

admin.site.register(Result)
admin.site.register(Category_Result)
admin.site.register(Session_Answer)
admin.site.register(AssessmentImages)
admin.site.register(AssessmentMedia)
admin.site.register(AssessmentFeedback)
