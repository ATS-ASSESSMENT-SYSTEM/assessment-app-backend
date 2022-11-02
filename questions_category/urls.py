from django.urls import path

from .views import (
    CategoryListCreateAPIView, CategoryRetrieveUpdateDeleteAPIView,
    QuestionCreateAPIView, QuestionListAPIView
)


urlpatterns = [
    path('', CategoryListCreateAPIView.as_view(), name='category-list-create-view'),
    path('<int:pk>/', CategoryRetrieveUpdateDeleteAPIView.as_view(), name='category-retrieve-update-view'),
    path('<int:pk>/questions/', QuestionCreateAPIView.as_view(), name='question-create-view'),
    path('<int:pk>/questionslist/', QuestionListAPIView.as_view(), name='question-list-view'),
]