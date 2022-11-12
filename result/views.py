from django.db.models import Sum

from rest_framework import status
from rest_framework.generics import (
    ListCreateAPIView, RetrieveUpdateDestroyAPIView, CreateAPIView, ListAPIView
)
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, JSONParser, FormParser

from result.models import Result, Category_Result, AssessmentImages
from assessment.models import AssessmentSession
from .api.serializers import ResultSerializer, CandidateResultSerializer, SessionAnswerSerializer, \
    SessionProcessorSerializer, AssessmentImageSerializer
from utils.json_renderer import CustomRenderer
from .api.perms_and_mixins import MultipleFieldLookupMixin


class AddResultAPIView(CreateAPIView):
    serializer_class = ResultSerializer
    renderer_classes = (CustomRenderer,)


class AddResultSummaryAPIView(APIView):
    serializer_class = ''
    renderer_classes = (CustomRenderer,)


class CandidatesResultAPIView(ListAPIView):
    filter_backends = [DjangoFilterBackend]


class CandidateResultAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = CandidateResultSerializer
    renderer_classes = (CustomRenderer,)
    # lookup_field = ('candidate', 'id')

    # def get_queryset(self):
    #     pk = self.kwargs.get('pk')
    #     result = self.get_queryset()
    #     q = Category_Result.objects.(result=pk)
    #     result['scores'] = q
    #     result['total'] = q.aggregate(sum=Sum('score'))
    #     return result


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


class AssessmentProcessorAPIView(APIView):
    renderer_classes = (CustomRenderer,)


class AssessmentImagesAPIView(APIView):
    serializer_class = AssessmentImageSerializer
    renderer_classes = (CustomRenderer,)
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            session = AssessmentSession.objects.get(session=request.data.session)
            session_images = AssessmentImages(assessment=session.assessment,
                                              category=session.category,
                                              candidate=session.candidate,
                                              images=request.data.get('image')
                                              )
            session_images.save()
            return Response(serializer.data, status=status.HTTP_201_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


