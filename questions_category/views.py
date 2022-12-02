import json
from django.shortcuts import render, get_object_or_404

# Create your views here.
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import (
    ListCreateAPIView, RetrieveUpdateDestroyAPIView, CreateAPIView, ListAPIView, UpdateAPIView, GenericAPIView,
)
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from utils.json_renderer import CustomRenderer
from questions_category.models import Category, Question, Choice
from questions_category.serializers import CategorySerializer, QuestionSerializer, ChoiceSerializer
from utils.middleware import AESCipherMiddleware


class MultipleFieldLookupMixin:
    def get_object(self):
        queryset = self.get_queryset()  # Get the base queryset
        queryset = self.filter_queryset(queryset)  # Apply any filter backends
        filter = {}
        for field in self.lookup_fields:
            if self.kwargs.get(field):  # Ignore empty fields.
                filter[field] = self.kwargs[field]
        obj = get_object_or_404(queryset, **filter)  # Lookup the object
        self.check_object_permissions(self.request, obj)
        return obj


class StandardPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 10


class CategoryListCreateAPIView(ListCreateAPIView):
    serializer_class = CategorySerializer
    queryset = Category.active_objects.all()
    renderer_classes = (CustomRenderer,)


class CategoryRetrieveUpdateDeleteAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = CategorySerializer
    queryset = Category.active_objects.all()
    renderer_classes = (CustomRenderer,)

    def delete(self, request, *args, **kwargs):
        category_id = self.kwargs.get('pk')
        try:
            category = Category.objects.get(id=category_id)
            category.is_delete = not category.is_delete
            category.save()
            if category.is_delete:
                return Response({"data": "Deleted Successfully"}, status=status.HTTP_200_OK)
            return Response({"data": "Retrieved Successfully"}, status=status.HTTP_200_OK)
        except Category.DoesNotExist:
            raise ValidationError('Category does not exist.')


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
    filterset_fields = ['test_category', 'question_type', 'question_category']
    renderer_classes = (CustomRenderer,)

    def get_queryset(self):
        category_pk = self.kwargs.get('pk')
        return Question.active_objects.filter(test_category__pk=category_pk)


class QuestionRetrieveUpdateDeleteAPIView(MultipleFieldLookupMixin, RetrieveUpdateDestroyAPIView):
    serializer_class = QuestionSerializer
    renderer_classes = (CustomRenderer,)
    lookup_fields = ('test_category_id', 'id')

    def get_queryset(self):
        category_id = self.kwargs.get('test_category_id')
        return Question.active_objects.filter(test_category__pk=category_id)

    def delete(self, request, *args, **kwargs):
        question_id = self.kwargs.get('id')
        try:
            question = Question.objects.get(id=question_id)
            question.is_delete = not question.is_delete
            question.save()
            if question.is_delete:
                return Response({"data": "Deleted Successfully"}, status=status.HTTP_200_OK)
            return Response({"data": "Retrieved Successfully"}, status=status.HTTP_200_OK)
        except Question.DoesNotExist:
            raise ValidationError('Question does not exist.')


class UpdateChoiceAPIView(MultipleFieldLookupMixin, RetrieveUpdateDestroyAPIView):
    serializer_class = ChoiceSerializer
    renderer_classes = (CustomRenderer,)
    lookup_fields = ('question_id', 'id')

    def get_queryset(self):
        question_id = self.kwargs.get('question_id')
        return Choice.active_objects.filter(question_id=question_id)

    def delete(self, request, *args, **kwargs):
        choice_id = self.kwargs.get('id')
        try:
            choice = Choice.objects.get(id=choice_id)
            choice.is_delete = not choice.is_delete
            choice.save()
            if choice.is_delete:
                return Response({"data": "Deleted Successfully"}, status=status.HTTP_200_OK)
            return Response({"data": "Retrieved Successfully"}, status=status.HTTP_200_OK)
        except Choice.DoesNotExist:
            raise ValidationError('Choice does not exist.')
