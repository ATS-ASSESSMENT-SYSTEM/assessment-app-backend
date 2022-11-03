from django.shortcuts import render
from assessment.models import Assessment
from assessment.serializers import AssessmentSerializer, CategorySerializer
from rest_framework import generics
from questions_category.models import Category
from utils.json_renderer import CustomRenderer



# Create your views here.

class AssessmentList(generics.ListCreateAPIView):
    queryset = Assessment.active_objects.all()
    serializer_class = AssessmentSerializer
    renderer_classes = (CustomRenderer,)
    
class AssesmentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Assessment.active_objects.all()
    serializer_class = AssessmentSerializer
    renderer_classes = (CustomRenderer,)
    
class CategoryList(generics.ListAPIView):
    serializer_class = CategorySerializer
    renderer_classes = (CustomRenderer,)
    
    def get_queryset(self):
        assessment_pk = self.kwargs.get('pk')
        return Category.objects.filter(assessment__pk=assessment_pk)
    
    
