import uuid

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from questions_category.models import Category, Question
from django.core.validators import MaxValueValidator, MinValueValidator
# Create your models here.

class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_delete=False)

class DeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_delete=True)
    
    
class ApplicationType(models.Model):
    title = models.CharField(max_length=250)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_delete = models.BooleanField(default=False)
    
    objects = models.Manager()
    active_objects = ActiveManager()
    deleted_objects = DeleteManager()
    

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return self.title
    

class Assessment(models.Model):
    name = models.CharField(max_length=200)
    instruction = models.TextField(null=True, blank=False)
    application_type = models.ForeignKey(ApplicationType, on_delete=models.CASCADE)
    date_created = models.DateField(auto_now_add=True)
    date_updated = models.DateField(auto_now=True)
    benchmark = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    is_delete = models.BooleanField(default=False)
    
    objects = models.Manager()
    active_objects = ActiveManager()
    deleted_objects = DeleteManager()
    
    def __str__(self):
        return f'Assessment for {self.application_type}'
    
    class Meta:
        ordering = ["-date_created"]
        
        
class AssessmentSession(models.Model):
   assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
   session_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
   category = models.ForeignKey(Category, on_delete=models.CASCADE)
   question_list = models.ManyToManyField(Question)
   candidate = models.CharField(max_length=200)

