from django.urls import path

from .views import AddResultAPIView, CandidateResultAPIView,\
    SessionAnswerAPIView, SessionProcessorAPIView, AssessmentImagesAPIView

urlpatterns = [
    path('create', AddResultAPIView.as_view(), name='add-result'),
    path('<int:pk>', CandidateResultAPIView.as_view(), name='candidate-result'),
    path('save_answer', SessionAnswerAPIView.as_view(), name='save-session-answer'),
    path('save_session', SessionProcessorAPIView.as_view(), name='save-section'),
    path('save_image', AssessmentImagesAPIView.as_view(), name='save-image')
]
