from django.shortcuts import render

# Create your views here.
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.generics import (
    ListCreateAPIView, RetrieveUpdateDestroyAPIView, CreateAPIView, ListAPIView
)
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from utils.json_renderer import CustomRenderer
from questions_category.models import Category, Question
from questions_category.serializers import CategorySerializer, QuestionSerializer


class StandardPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 10


class CategoryListCreateAPIView(ListCreateAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()


class CategoryRetrieveUpdateDeleteAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()


class QuestionCreateAPIView(CreateAPIView):
    serializer_class = QuestionSerializer
    renderer_classes = (CustomRenderer,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class QuestionListAPIView(ListAPIView):
    serializer_class = QuestionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['test_category', 'question_type', 'difficult']
    renderer_classes = (CustomRenderer,)

    def get_queryset(self):
        category_pk = self.kwargs.get('pk')
        return Question.objects.filter(test_category__pk=category_pk)
