import json
from datetime import datetime

from django.shortcuts import render
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q

from app_core.permissions import IsApplicationBackendAuthenticated, IsAssessmentFrontendAuthenticated, \
    IsAssessmentAdminAuthenticated, IsApplicationBackendOrIsAssessmentAdminAuthenticated
from assessment.models import Assessment, ApplicationType, AssessmentSession
from assessment.serializers import AssessmentSerializer, CategorySerializer, ApplicationTypeSerializer, \
    StartAssessmentSerializer, GetAssessmentForCandidateSerializer, CheckAssessmentDurationSerializer
from rest_framework import generics, status
from questions_category.models import Category, OpenEndedAnswer
from result.models import SessionAnswer, Result, CategoryResult
from utils.json_renderer import CustomRenderer

from questions_category.views import MultipleFieldLookupMixin
from questions_category.serializers import QuestionSerializer, GenerateQuestionSerializer, SessionAnswerSerializer, \
    OpenEndedAnswerSerializer
from questions_category.models import Question

# Create your views here.
from utils.utils import CustomRetrieveUpdateDestroyAPIView, CustomListCreateAPIView, decrypt


class AssessmentList(CustomListCreateAPIView):
    queryset = Assessment.active_objects.all()
    serializer_class = AssessmentSerializer
    renderer_classes = (CustomRenderer,)
    permission_classes = (IsAssessmentAdminAuthenticated,)


class AssesmentDetail(CustomRetrieveUpdateDestroyAPIView):
    queryset = Assessment.active_objects.all()
    serializer_class = AssessmentSerializer
    renderer_classes = (CustomRenderer,)
    permission_classes = (IsAssessmentAdminAuthenticated,)

    def delete(self, request, *args, **kwargs):
        assessment_id = self.kwargs.get('pk')
        try:
            assessment = Assessment.objects.get(id=assessment_id)
            assessment.is_delete = not assessment.is_delete
            assessment.save()
            if assessment.is_delete:
                return Response({"data": "Deleted Successfully"}, status=status.HTTP_200_OK)
            return Response({"data": "Retrieved Successfully"}, status=status.HTTP_200_OK)
        except Assessment.DoesNotExist:
            raise ValidationError('Assessment does not exist.')


class AddCategoryToAssessmentAPIView(CustomRetrieveUpdateDestroyAPIView):
    queryset = Category.active_objects.all()
    renderer_classes = (CustomRenderer,)
    permission_classes = (IsAssessmentAdminAuthenticated,)

    def patch(self, request, assessment_id, id):
        try:
            assessment = Assessment.active_objects.get(id=assessment_id)
            category = Category.active_objects.get(id=id)
        except (Assessment.DoesNotExist, Category.DoesNotExist):
            raise ValidationError('Assessment or The Category does not exist.')
        else:
            if not assessment.category.filter(assessment__category=category).exists():
                assessment.category.add(category)
                assessment.save()
                return Response({'status': 'Success', 'message': 'Category added successfully.'})
            else:
                assessment.category.remove(category)
                assessment.save()
                return Response({'status': 'Success', 'message': 'Category removed'})


class GenerateRandomQuestions(CustomListCreateAPIView):
    serializer_class = StartAssessmentSerializer
    renderer_classes = (CustomRenderer,)
    permission_classes = (IsAssessmentFrontendAuthenticated,)

    def post(self, request, assessment_id, category_id):
        if request.data.get('data'):
            try:
                data = decrypt(request.data['data'])
                request._full_data = data
                serializer = self.get_serializer(data=request.data)
                if serializer.is_valid():
                    try:
                        assessment = Assessment.active_objects.get(id=assessment_id)
                        category = Category.active_objects.get(id=category_id)
                        current_session = AssessmentSession.active_objects.filter(assessment=assessment,
                                                                                  category=category,
                                                                                  candidate_id=serializer.data.get(
                                                                                      'candidate_id'))
                        check_session = AssessmentSession.active_objects.filter(assessment=assessment,
                                                                                candidate_id=serializer.data.get(
                                                                                    'candidate_id')).order_by(
                            'date_created').first()
                        if check_session:
                            if ((
                                        timezone.now() - check_session.date_created).total_seconds() / 3600) > assessment.total_duration:
                                return Response({'error': "Your assessment session has expired."},
                                                status=status.HTTP_403_FORBIDDEN)

                        if current_session.exists():
                            questions = current_session.first().question_list.all()
                            session = current_session.first()
                            answers = SessionAnswer.objects.filter(session=current_session.first().session_id,
                                                                   candidate=serializer.data.get('candidate_id'))
                            open_ended_answer = OpenEndedAnswer.active_objects.filter(
                                candidate=serializer.data.get('candidate_id'), category=category)
                            q_answers = SessionAnswerSerializer(answers, many=True)
                            q_open_ended_answer = OpenEndedAnswerSerializer(open_ended_answer, many=True)
                            q = GenerateQuestionSerializer(questions, many=True)
                            dump_session = json.dumps(str(session.session_id))
                            serialize_session = json.loads(dump_session)
                            return Response(
                                {'session_id': serialize_session, 'questions': q.data, 'answers': q_answers.data,
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
                            dump_session = json.dumps(str(session.session_id))
                            serialize_session = json.loads(dump_session)
                            q = GenerateQuestionSerializer(questions, many=True)
                            return Response({'session_id': serialize_session, 'questions': q.data},
                                            status=status.HTTP_200_OK)

                    except (
                            Assessment.DoesNotExist, Category.DoesNotExist, AssessmentSession.DoesNotExist,
                            Question.DoesNotExist):
                        raise ValidationError('Assessment or the category does not exist.')

                return Response({'error': serializer.errors})
            except ValueError:
                return Response('Padding incorrect, Encryption and Decryption key and vector must be same.',
                                status=status.HTTP_400_BAD_REQUEST)
        return Response('Data must be encrypted', status=status.HTTP_400_BAD_REQUEST)


class ApplicationTypeCreate(CustomListCreateAPIView):
    queryset = ApplicationType.active_objects.all()
    serializer_class = ApplicationTypeSerializer
    renderer_classes = (CustomRenderer,)
    permission_classes = (IsApplicationBackendAuthenticated,)


class ApplicationTypeList(ListAPIView):
    queryset = ApplicationType.active_objects.all()
    serializer_class = ApplicationTypeSerializer
    renderer_classes = (CustomRenderer,)
    permission_classes = (IsApplicationBackendOrIsAssessmentAdminAuthenticated,)


class ApplicationTypeDetail(CustomRetrieveUpdateDestroyAPIView):
    queryset = ApplicationType.active_objects.all()
    serializer_class = ApplicationTypeSerializer
    renderer_classes = (CustomRenderer,)
    permission_classes = (IsApplicationBackendAuthenticated,)
    lookup_field = 'uid'

    def delete(self, request, *args, **kwargs):
        application_type_id = self.kwargs.get('uid')
        try:
            application_type = ApplicationType.objects.get(uid=application_type_id)
            application_type.is_delete = not application_type.is_delete
            application_type.save()
            if application_type.is_delete:
                return Response({"data": "Deleted Successfully"}, status=status.HTTP_200_OK)
            return Response({"data": "Retrieved Successfully"}, status=status.HTTP_200_OK)
        except ApplicationType.DoesNotExist:
            raise ValidationError('ApplicationType does not exist.')


class GetAssessmentForCandidateAPIView(CustomListCreateAPIView):
    serializer_class = GetAssessmentForCandidateSerializer
    renderer_classes = (CustomRenderer,)
    permission_classes = (IsAssessmentFrontendAuthenticated,)

    def post(self, request):
        if request.data.get('data'):
            try:
                data = decrypt(request.data['data'])
                request._full_data = data
                serializer = self.get_serializer(data=request.data)
                if serializer.is_valid():
                    try:
                        application_type = ApplicationType.active_objects.get(
                            title__iexact=serializer.data.get('course'))
                        assessment = Assessment.active_objects.filter(application_type=application_type).latest(
                            'date_created')
                        assessment_data = AssessmentSerializer(assessment)
                        return Response(assessment_data.data,
                                        status=status.HTTP_200_OK)
                    except (ApplicationType.DoesNotExist, Assessment.DoesNotExist):
                        raise ValidationError('ApplicationType or Assessment does not exist.')
                return Response({'error': serializer.errors})
            except ValueError:
                return Response('Padding incorrect, Encryption and Decryption key and vector must be same.',
                                status=status.HTTP_400_BAD_REQUEST)
        return Response('Data must be encrypted', status=status.HTTP_400_BAD_REQUEST)


class CheckAssessmentDurationAPIView(CustomListCreateAPIView):
    serializer_class = CheckAssessmentDurationSerializer
    renderer_classes = (CustomRenderer,)
    permission_classes = (IsAssessmentFrontendAuthenticated,)

    def post(self, request):
        if request.data.get('data'):
            try:
                data = decrypt(request.data['data'])
                request._full_data = data
                serializer = self.get_serializer(data=request.data)
                if serializer.is_valid():
                    try:
                        application_type = ApplicationType.active_objects.get(
                            title__iexact=serializer.data.get('course'))
                        assessment = Assessment.active_objects.filter(application_type=application_type).latest(
                            'date_created')
                        assessment_session = AssessmentSession.active_objects.filter(assessment=assessment,
                                                                                     candidate_id=serializer.data.get(
                                                                                         'candidate_id')).order_by(
                            'date_created')
                        result = Result.objects.filter(assessment=assessment,
                                                       candidate=serializer.data.get('candidate_id'))
                        category_result = CategoryResult.objects.filter(result=result.first())
                        if assessment_session.exists():
                            if ((
                                        timezone.now() - assessment_session.first().date_created).total_seconds() / 3600) > assessment.total_duration:
                                return Response({'error': "Your assessment session has expired."},
                                                status=status.HTTP_403_FORBIDDEN)
                        if result.exists():
                            if assessment.category.count() == category_result.count():
                                return Response('Assessment has already been taken by the candidate.',
                                                status=status.HTTP_400_BAD_REQUEST)

                    except (ApplicationType.DoesNotExist, Assessment.DoesNotExist, AssessmentSession.DoesNotExist,
                            Result.DoesNotExist, CategoryResult.DoesNotExist):
                        raise ValidationError('ApplicationType or Assessment does not exist.')
                return Response({'error': serializer.errors})
            except ValueError:
                return Response('Padding incorrect, Encryption and Decryption key and vector must be same.',
                                status=status.HTTP_400_BAD_REQUEST)
        return Response('Data must be encrypted', status=status.HTTP_400_BAD_REQUEST)
