from django.shortcuts import render

from rest_framework import status
from rest_framework.generics import (
    ListCreateAPIView, RetrieveUpdateDestroyAPIView, CreateAPIView, ListAPIView
)
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response

from result.models import Result
from .api.serializers import ResultSerializer
from utils.json_renderer import CustomRenderer


class AddResultAPIView(CreateAPIView):
    serializer_class = ResultSerializer
    renderer_classes = (CustomRenderer,)


class ResultAPIView(RetrieveUpdateDestroyAPIView):
    pass
