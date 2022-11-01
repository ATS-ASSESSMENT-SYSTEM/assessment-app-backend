from django.urls import path

from .views import (
    CategoryListCreateAPIView,
)


urlpatterns = [
    path('', CategoryListCreateAPIView.as_view(), name='category-list-create-view'),
]