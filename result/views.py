from django.db.models import Sum

from rest_framework import status
from rest_framework.generics import (
    ListCreateAPIView, RetrieveUpdateDestroyAPIView, CreateAPIView, ListAPIView
)
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, JSONParser, FormParser

from result.models import Result, Category_Result, AssessmentImages, AssessmentFeedback
from assessment.models import AssessmentSession

from .api.serializers import CandidateResultSerializer, SessionAnswerSerializer, \
    SessionProcessorSerializer, AssessmentImageSerializer, ResultListSerializer, AssessmentMediaSerializer, \
    AssessmentFeedbackSerializer, CandidateResultSerializer, \
    ProcessOpenEndedAnswerSerializer, ResultInitializerSerializer
from utils.json_renderer import CustomRenderer
from .api.perms_and_mixins import MultipleFieldLookupMixin
from app_core.permissions import IsAssessmentAdminAuthenticated


class SessionAnswerAPIView(CreateAPIView):
    serializer_class = SessionAnswerSerializer
    renderer_classes = (CustomRenderer,)


class SessionProcessorAPIView(APIView):
    serializer_class = SessionProcessorSerializer
    renderer_classes = (CustomRenderer,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AssessmentImagesAPIView(APIView):
    serializer_class = AssessmentImageSerializer
    renderer_classes = (CustomRenderer,)
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        # print(request.data['session_id'])
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            session = AssessmentSession.objects.get(session_id=request.data['session_id'])
            session_images = AssessmentImages(assessment=session.assessment,
                                              category=session.category,
                                              candidate=session.candidate_id,
                                              image=request.data.get('image')
                                              )
            session_images.save()
            print(session_images.image)
            return Response("uploaded", status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResultLIstAPIView(ListAPIView):
    queryset = Result.objects.all()
    renderer_classes = (CustomRenderer,)
    serializer_class = ResultListSerializer
    filter_backends = [DjangoFilterBackend]
    filter_fields = ['status', 'assessment']


class AssessmentMediaAPIView(CreateAPIView):
    serializer_class = AssessmentMediaSerializer
    renderer_classes = (CustomRenderer,)
    parser_classes = (MultiPartParser, FormParser)


class AssessmentFeedbackAPIView(CreateAPIView):
    serializer_class = AssessmentFeedbackSerializer
    renderer_classes = (CustomRenderer,)


class CandidateResultAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Result.objects.all()
    # permission_classes = (IsAssessmentAdminAuthenticated,)
    serializer_class = CandidateResultSerializer
    renderer_classes = (CustomRenderer,)


class ProcessOpenEndedAPIView(APIView):
    renderer_classes = (CustomRenderer,)
    serializer_class = ProcessOpenEndedAnswerSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResultInitializerAPIView(APIView):
    renderer_classes = (CustomRenderer,)
    serializer_class = ResultInitializerSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
