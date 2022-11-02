from django.db import models
# Create your models here.

class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_delete=False)

class DeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_delete=True)

class Assessment(models.Model):
    name = models.CharField(max_length=200)
    instruction = models.TextField(null=True, blank=False)
    application_type = models.CharField(max_length=200)
    date_created = models.DateField(auto_now_add=True)
    date_updated = models.DateField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    
    objects = models.Manager()
    active_objects = ActiveManager()
    deleted_objects = DeleteManager()
    
    def __str__(self):
        return f'Assessment for {self.application_type}'
    
    class Meta:
        ordering = ["-date_created"]