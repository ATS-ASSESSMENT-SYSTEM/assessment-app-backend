from datetime import datetime

from django.shortcuts import render
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q

from assessment.models import Assessment, ApplicationType, AssessmentSession
from assessment.serializers import AssessmentSerializer, CategorySerializer, ApplicationTypeSerializer, \
    StartAssessmentSerializer, GetAssessmentForCandidateSerializer
from rest_framework import generics, status
from questions_category.models import Category, OpenEndedAnswer
from result.models import Session_Answer
from utils.json_renderer import CustomRenderer

from questions_category.views import MultipleFieldLookupMixin
from questions_category.serializers import QuestionSerializer, GenerateQuestionSerializer, SessionAnswerSerializer, \
    OpenEndedAnswerSerializer
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

    def delete(self, request, *args, **kwargs):
        assessment_id = self.kwargs.get('pk')
        try:
            assessment = Assessment.active_objects.get(id=assessment_id)
            assessment.is_delete = True
            assessment.save()
            return Response({"data": "Deleted Successfully"}, status=status.HTTP_200_OK)
        except Assessment.DoesNotExist:
            raise ValidationError('Assessment does not exist.')


class CategoryList(generics.ListAPIView):
    serializer_class = CategorySerializer
    renderer_classes = (CustomRenderer,)

    def get_queryset(self):
        assessment_pk = self.kwargs.get('pk')
        return Category.active_objects.filter(assessment__pk=assessment_pk)


class AddCategoryToAssessmentAPIView(generics.UpdateAPIView):
    queryset = Category.active_objects.all()
    renderer_classes = (CustomRenderer,)

    def patch(self, request, assessment_id, id):
        try:
            assessment = Assessment.active_objects.get(id=assessment_id)
            category = Category.active_objects.get(id=id)
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
                assessment = Assessment.active_objects.get(id=assessment_id)
                category = Category.active_objects.get(id=category_id)
                current_session = AssessmentSession.active_objects.filter(assessment=assessment, category=category,
                                                                          candidate_id=serializer.data.get(
                                                                              'candidate_id'))
                check_session = AssessmentSession.active_objects.filter(assessment=assessment,
                                                                        candidate_id=serializer.data.get(
                                                                            'candidate_id')).order_by(
                    'date_created')

                if check_session.exists():
                    if ((
                                timezone.now() - check_session.first().date_created).total_seconds() / 3600) > assessment.total_duration:
                        return Response({'error': "Your assessment session has expired."},
                                        status=status.HTTP_403_FORBIDDEN)

                if current_session.exists():
                    questions = current_session.first().question_list.all()
                    session = current_session.first()
                    answers = Session_Answer.objects.filter(session=current_session.first().session_id,
                                                            candidate=serializer.data.get('candidate_id'))
                    open_ended_answer = OpenEndedAnswer.active_objects.filter(
                        candidate=serializer.data.get('candidate_id'), category=category)
                    q_answers = SessionAnswerSerializer(answers, many=True)
                    q_open_ended_answer = OpenEndedAnswerSerializer(open_ended_answer, many=True)
                    q = GenerateQuestionSerializer(questions, many=True)
                    return Response({'session_id': session.session_id, 'questions': q.data, 'answers': q_answers.data,
                                     'open_ended_answers': q_open_ended_answer.data},
                                    status=status.HTTP_200_OK)
                else:
                    session = AssessmentSession.objects.create(assessment=assessment,
                                                               category=category, **serializer.data)

                    questions = Question.active_objects.filter(test_category__assessment=assessment,
                                                               test_category=category,
                                                               question_category="Real").order_by(
                        '?')[
                                :category.num_of_questions]

                    for question in questions:
                        session.question_list.add(question)

                    q = GenerateQuestionSerializer(questions, many=True)
                    return Response({'session_id': session.session_id, 'questions': q.data},
                                    status=status.HTTP_200_OK)

            except (
                    Assessment.DoesNotExist, Category.DoesNotExist, AssessmentSession.DoesNotExist,
                    Question.DoesNotExist):
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
    lookup_field = 'uid'

    def delete(self, request, *args, **kwargs):
        application_type_id = self.kwargs.get('pk')
        try:
            application_type = ApplicationType.active_objects.get(id=application_type_id)
            application_type.is_delete = True
            application_type.save()
            return Response({"data": "Deleted Successfully"}, status=status.HTTP_200_OK)
        except ApplicationType.DoesNotExist:
            raise ValidationError('ApplicationType does not exist.')


class GetAssessmentForCandidateAPIView(GenericAPIView):
    serializer_class = GetAssessmentForCandidateSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                application_type = ApplicationType.active_objects.get(title__iexact=serializer.data.get('course'))
                assessment = Assessment.active_objects.filter(application_type=application_type).latest('date_created')
                assessment_data = AssessmentSerializer(assessment)
                return Response({'data': assessment_data.data},
                                status=status.HTTP_200_OK)
            except (ApplicationType.DoesNotExist, Assessment.DoesNotExist):
                raise ValidationError('ApplicationType or Assessment does not exist.')
        return Response({'error': serializer.errors})
