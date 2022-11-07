from django.shortcuts import render, get_object_or_404

# Create your views here.
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.generics import (
    ListCreateAPIView, RetrieveUpdateDestroyAPIView, CreateAPIView, ListAPIView, UpdateAPIView
)
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from utils.json_renderer import CustomRenderer
from questions_category.models import Category, Question, Choice
from questions_category.serializers import CategorySerializer, QuestionSerializer, ChoiceSerializer


class MultipleFieldLookupMixin:
    def get_object(self):
        queryset = self.get_queryset()  # Get the base queryset
        queryset = self.filter_queryset(queryset)  # Apply any filter backends
        filter = {}
        for field in self.lookup_fields:
            if self.kwargs.get(field):  # Ignore empty fields.
                filter[field] = self.kwargs[field]
                print(filter[field])
        obj = get_object_or_404(queryset, **filter)  # Lookup the object
        self.check_object_permissions(self.request, obj)
        return obj


class StandardPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 10


class CategoryListCreateAPIView(ListCreateAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    renderer_classes = (CustomRenderer,)


class CategoryRetrieveUpdateDeleteAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    renderer_classes = (CustomRenderer,)


class QuestionCreateAPIView(CreateAPIView):
    serializer_class = QuestionSerializer
    renderer_classes = (CustomRenderer,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        print(serializer)
        if serializer.is_valid():
            serializer.save()
            print(serializer.data)
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


class QuestionRetrieveUpdateDeleteAPIView(MultipleFieldLookupMixin, RetrieveUpdateDestroyAPIView):
    serializer_class = QuestionSerializer
    renderer_classes = (CustomRenderer,)
    lookup_fields = ('test_category_id', 'id')

    def get_queryset(self):
        category_id = self.kwargs.get('test_category_id')
        return Question.objects.filter(test_category__pk=category_id)


class UpdateChoiceAPIView(UpdateAPIView):
    serializer_class = ChoiceSerializer
    queryset = Choice.objects.all()


