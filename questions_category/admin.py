from django.contrib import admin
from questions_category.models import Category, Choice, Question, OpenEndedAnswer
# Register your models here.
admin.site.register(Category)
admin.site.register(Choice)
admin.site.register(Question)
# admin.site.register(OpenEndedAnswer)

