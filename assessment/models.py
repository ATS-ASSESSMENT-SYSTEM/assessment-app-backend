from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_delete=False)

class DeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_delete=True)

class Assessment(models.Model):
    name = models.CharField(max_length=200, null=True)
    application_type = models.CharField(max_length=200, null=True)
    date_created = models.DateField(auto_now_add=True)
    date_updated = models.DateField(auto_now=True)
    is_delete = models.BooleanField(default=False)
    
    objects = models.Manager()
    active_objects = ActiveManager()
    deleted_objects = DeleteManager()
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ["-date_created"]