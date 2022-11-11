from django.shortcuts import render
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q

from assessment.models import Assessment, ApplicationType, AssessmentSession
from assessment.serializers import AssessmentSerializer, CategorySerializer, ApplicationTypeSerializer, \
    StartAssessmentSerializer
from rest_framework import generics, status
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


class AddCategoryToAssessmentAPIView(generics.UpdateAPIView):
    queryset = Category.objects.all()
    renderer_classes = (CustomRenderer,)

    def patch(self, request, assessment_id, id):
        try:
            assessment = Assessment.active_objects.get(id=assessment_id)
            category = Category.objects.get(id=id)
        except (Assessment.DoesNotExist, Category.DoesNotExist):
            raise ValidationError('Assessment or The Category does not exist.')
        else:
            if assessment not in category.assessment.all():
                if assessment.category_set.count() < 5:
                    print(assessment.category_set.all().count())
                    category.assessment.add(assessment)
                    category.save()
                    return Response({'status': 'Success', 'message': 'Category added successfully.'})
                return Response({'status': 'Error', 'message': 'Categories cannot be more than 5 for a assessment.'})
            else:
                category.assessment.remove(assessment)
                category.save()
                return Response({'status': 'Success', 'message': 'Category removed'})


class GenerateRandomQuestions(generics.CreateAPIView):
    serializer_class = StartAssessmentSerializer
    renderer_classes = (CustomRenderer,)

    
    def post(self, request, assessment_id, category_id):
        serializer = self.get_serializer(data=request.data)
        print(assessment_id)
        print(category_id)
        if serializer.is_valid():
            try:
                assessment = Assessment.objects.get(id=assessment_id)
                print(assessment)
                category = Category.objects.get(id=category_id)
                print(category)
                session = AssessmentSession.objects.filter(assessment=assessment, category=category,
                                                    candidate=serializer.data.get('applicant_id'))
                if session.exists():
                    questions = session.first().question_list.all()
                else:
                    questions = Question.objects.filter(test_category__assessment=assessment,
                                                        test_category=category).order_by('?')[:category.num_of_questions]
                    new_session = AssessmentSession.objects.create(assessment=assessment, category=category,
                                                            candidate=serializer.data['applicant_id'])
                    for question in category.question_set.all():
                        new_session.question_list.add(question)
            except (Assessment.DoesNotExist, Category.DoesNotExist):
                raise ValidationError('Assessment or the category does not exist.')
            else:
                print(questions)
                q = QuestionSerializer(questions, many=True)
                print(q)
                return Response(q.data, status=status.HTTP_200_OK)
        return Response({'error': serializer.errors})


class ApplicationTypeList(generics.ListCreateAPIView):
    queryset = ApplicationType.active_objects.all()
    serializer_class = ApplicationTypeSerializer
    renderer_classes = (CustomRenderer,)


class ApplicationTypeDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ApplicationType.active_objects.all()
    serializer_class = ApplicationTypeSerializer
    renderer_classes = (CustomRenderer,)


