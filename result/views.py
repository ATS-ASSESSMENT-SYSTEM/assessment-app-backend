from django.db.models import Sum

from rest_framework import status
from rest_framework.generics import (
    ListCreateAPIView, RetrieveUpdateDestroyAPIView, CreateAPIView, ListAPIView
)
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, JSONParser, FormParser

from result.models import Result, CategoryResult, AssessmentImages, AssessmentFeedback
from assessment.models import AssessmentSession

from .api.serializers import CandidateResultSerializer, SessionAnswerSerializer, \
    SessionProcessorSerializer, AssessmentImageSerializer, ResultListSerializer, AssessmentMediaSerializer, \
    AssessmentFeedbackSerializer, CandidateResultSerializer, \
    ProcessOpenEndedAnswerSerializer, ResultInitializerSerializer
from utils.json_renderer import CustomRenderer
from .api.perms_and_mixins import MultipleFieldLookupMixin
from app_core.permissions import IsAssessmentAdminAuthenticated, IsAssessmentFrontendAuthenticated
from utils.utils import CustomRetrieveUpdateDestroyAPIView, CustomListCreateAPIView, decrypt


class SessionAnswerAPIView(CustomListCreateAPIView):
    serializer_class = SessionAnswerSerializer
    renderer_classes = (CustomRenderer,)
    permission_classes = (IsAssessmentFrontendAuthenticated,)

    def post(self, request, *args, **kwargs):
        if request.data.get('data'):
            try:
                data = decrypt(request.data['data'])
                request._full_data = data
                serializer = self.get_serializer(data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return Response('Answer saved.', status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except ValueError:
                return Response('Padding incorrect, Encryption and Decryption key and vector must be same.',
                                status=status.HTTP_400_BAD_REQUEST)
        return Response('Data must be encrypted', status=status.HTTP_400_BAD_REQUEST)



class SessionProcessorAPIView(CustomListCreateAPIView):
    serializer_class = SessionProcessorSerializer
    renderer_classes = (CustomRenderer,)
    permission_classes = (IsAssessmentFrontendAuthenticated,)

    def post(self, request):
        if request.data.get('data'):
            try:
                data = decrypt(request.data['data'])
                request._full_data = data
                serializer = self.get_serializer(data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except ValueError:
                return Response('Padding incorrect, Encryption and Decryption key and vector must be same.',
                                status=status.HTTP_400_BAD_REQUEST)
        return Response('Data must be encrypted', status=status.HTTP_400_BAD_REQUEST)


class AssessmentImagesAPIView(CustomListCreateAPIView):
    serializer_class = AssessmentImageSerializer
    renderer_classes = (CustomRenderer,)
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = (IsAssessmentFrontendAuthenticated,)

    def post(self, request):
        if request.data.get('data'):
            try:
                data = decrypt(request.data['data'])
                request._full_data = data
                serializer = self.get_serializer(data=request.data)
                if serializer.is_valid():
                    session = AssessmentSession.objects.get(
                        session_id=request.data['session_id'])
                    session_images = AssessmentImages(assessment=session.assessment,
                                                      category=session.category,
                                                      candidate=session.candidate_id,
                                                      image=request.data.get('image')
                                                      )
                    session_images.save()
                    print(session_images.image)
                    return Response("uploaded", status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except ValueError:
                return Response('Padding incorrect, Encryption and Decryption key and vector must be same.',
                                status=status.HTTP_400_BAD_REQUEST)
        return Response('Data must be encrypted', status=status.HTTP_400_BAD_REQUEST)


class ResultLIstAPIView(CustomListCreateAPIView):
    queryset = Result.objects.all()
    renderer_classes = (CustomRenderer,)
    serializer_class = ResultListSerializer
    filter_backends = [DjangoFilterBackend]
    filter_fields = ['status', 'assessment']
    permission_classes = (IsAssessmentAdminAuthenticated,)


class AssessmentMediaAPIView(CustomListCreateAPIView):
    serializer_class = AssessmentMediaSerializer
    renderer_classes = (CustomRenderer,)
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = (IsAssessmentFrontendAuthenticated,)


class AssessmentFeedbackAPIView(CustomListCreateAPIView):
    serializer_class = AssessmentFeedbackSerializer
    renderer_classes = (CustomRenderer,)
    permission_classes = (IsAssessmentFrontendAuthenticated,)


class CandidateResultAPIView(CustomRetrieveUpdateDestroyAPIView):
    queryset = Result.objects.all()
    permission_classes = (IsAssessmentAdminAuthenticated,)
    serializer_class = CandidateResultSerializer
    renderer_classes = (CustomRenderer,)


class ProcessOpenEndedAPIView(CustomListCreateAPIView):
    renderer_classes = (CustomRenderer,)
    serializer_class = ProcessOpenEndedAnswerSerializer
    permission_classes = (IsAssessmentAdminAuthenticated,)

    def post(self, request):
        if request.data.get('data'):
            try:
                data = decrypt(request.data['data'])
                request._full_data = data
                serializer = self.get_serializer(data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except ValueError:
                return Response('Padding incorrect, Encryption and Decryption key and vector must be same.',
                                status=status.HTTP_400_BAD_REQUEST)
        return Response('Data must be encrypted', status=status.HTTP_400_BAD_REQUEST)


class ResultInitializerAPIView(CustomListCreateAPIView):
    renderer_classes = (CustomRenderer,)
    serializer_class = ResultInitializerSerializer
    permission_classes = (IsAssessmentFrontendAuthenticated,)

    def post(self, request):
        if request.data.get('data'):
            try:
                data = decrypt(request.data['data'])
                request._full_data = data
                serializer = self.get_serializer(data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except ValueError:
                return Response('Padding incorrect, Encryption and Decryption key and vector must be same.',
                                status=status.HTTP_400_BAD_REQUEST)
        return Response('Data must be encrypted', status=status.HTTP_400_BAD_REQUEST)
