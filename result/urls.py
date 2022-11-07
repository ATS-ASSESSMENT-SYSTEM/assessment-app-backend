from django.urls import path

from .views import AddResultAPIView, CandidateResultAPIView

urlpatterns = [
    path('create', AddResultAPIView.as_view(), name='add-result'),
    path('<int:pk>', CandidateResultAPIView.as_view(), name='candidate-result')
]
