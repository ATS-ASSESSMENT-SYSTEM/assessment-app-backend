from django.shortcuts import render
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q

from assessment.models import Assessment
from assessment.serializers import AssessmentSerializer, CategorySerializer
from rest_framework import generics
from questions_category.models import Category
from utils.json_renderer import CustomRenderer

from questions_category.views import MultipleFieldLookupMixin
from questions_category.serializers import QuestionSerializer
from questions_category.models import Question



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

class AddCategoryToAssessmentAPIView(MultipleFieldLookupMixin, generics.UpdateAPIView):
    queryset = Category.objects.all()
    lookup_fields = ('assessment_id', 'id')
    renderer_classes = (CustomRenderer,)

    def patch(self, request, assessment_id, id):
        try:
            assessment = Assessment.active_objects.get(id=assessment_id)
            category = Category.objects.get(id=id)
        except (Assessment.DoesNotExist, Category.DoesNotExist):
            raise ValidationError('Assessment or The Category does not exist.')
        else:
            if assessment not in category.assessment.all():
                category.assessment.add(assessment)
                category.save()
                return Response({'status': 'Success', 'message': 'Category added successfully.'})
            else:
                category.assessment.remove(assessment)
                category.save()
                return Response({'status': 'Success', 'message': 'Category removed'})
  
            
class GenerateRandomQuestions(generics.ListCreateAPIView):
    serializer_class = QuestionSerializer
    renderer_classes = (CustomRenderer,)
    def get_queryset(self):
        assessment_id = self.kwargs.get('assessment_id')
        category_id = self.kwargs.get('category_id')
        try:
            assessment = Assessment.objects.get(id=assessment_id)
            category = Category.objects.get(id=category_id)
            return Question.objects.filter(test_category__assessment=assessment, test_category=category).order_by('?')[:5]
        except (Assessment.DoesNotExist, Category.DoesNotExist):
            raise ValidationError('Assessment or the category does not exist.')


    
