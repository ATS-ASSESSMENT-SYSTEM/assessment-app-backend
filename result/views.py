from django.db.models import Sum

from rest_framework import status
from rest_framework.generics import (
    ListCreateAPIView, RetrieveUpdateDestroyAPIView, CreateAPIView, ListAPIView
)
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response

from result.models import Result, Category_Result
from .api.serializers import ResultSerializer, CandidateResultSerializer
from utils.json_renderer import CustomRenderer
from .api.perms_and_mixins import MultipleFieldLookupMixin


class AddResultAPIView(CreateAPIView):
    serializer_class = ResultSerializer
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


