from datetime import datetime

from django.shortcuts import render
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
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
from questions_category.serializers import QuestionSerializer, GenerateQuestionSerializer
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
            if category not in assessment.category.all():
                assessment.category.add(category)
                assessment.save()
                return Response({'status': 'Success', 'message': 'Category added successfully.'})
            else:
                assessment.category.remove(category)
                assessment.save()
                return Response({'status': 'Success', 'message': 'Category removed'})


class GenerateRandomQuestions(generics.CreateAPIView):
    serializer_class = StartAssessmentSerializer
    renderer_classes = (CustomRenderer,)

    def post(self, request, assessment_id, category_id):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                assessment = Assessment.objects.get(id=assessment_id)
                category = Category.objects.get(id=category_id)
                current_session = AssessmentSession.objects.filter(assessment=assessment, category=category,
                                                                   candidate_id=serializer.data.get('candidate_id'))
                check_session = AssessmentSession.objects.filter(assessment=assessment,
                                                                 candidate_id=serializer.data.get('candidate_id')).order_by(
                    'date_created')

                if check_session.exists():
                    if ((
                                timezone.now() - check_session.first().date_created).total_seconds() / 3600) > assessment.total_duration:
                        return Response({'error': "Your assessment session has expired."}, status=status.HTTP_403_FORBIDDEN)

                if current_session.exists():
                    questions = current_session.first().question_list.all()
                    session = current_session.first()
                else:
                    session = AssessmentSession.objects.create(assessment=assessment,
                                                               category=category, **serializer.data)

                    questions = Question.objects.filter(test_category__assessment=assessment,
                                                        test_category=category,
                                                        question_category="Real").order_by(
                        '?')[
                                :category.num_of_questions]

                    for question in category.questions.all():
                        session.question_list.add(question)

                q = GenerateQuestionSerializer(questions, many=True)
                return Response({'session_id': session.session_id, 'questions': q.data},
                                status=status.HTTP_200_OK)

            except (Assessment.DoesNotExist, Category.DoesNotExist):
                raise ValidationError('Assessment or the category does not exist.')

        return Response({'error': serializer.errors})


class ApplicationTypeList(generics.ListCreateAPIView):
    queryset = ApplicationType.active_objects.all()
    serializer_class = ApplicationTypeSerializer
    renderer_classes = (CustomRenderer,)


class ApplicationTypeDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ApplicationType.active_objects.all()
    serializer_class = ApplicationTypeSerializer
    renderer_classes = (CustomRenderer,)
