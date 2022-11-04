from django.shortcuts import render
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
 
from assessment.models import Assessment
from assessment.serializers import AssessmentSerializer, CategorySerializer
from rest_framework import generics
from questions_category.models import Category
from utils.json_renderer import CustomRenderer

from questions_category.views import MultipleFieldLookupMixin



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
        print(request.META)
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
