from django.shortcuts import render

# Create your views here.
from rest_framework.generics import (
    ListCreateAPIView,
)

from questions_category.models import Category
from questions_category.serializers import CategorySerializer


class CategoryListCreateAPIView(ListCreateAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()



