from django.urls import path

from .views import SessionAnswerAPIView, SessionProcessorAPIView, AssessmentImagesAPIView, \
    AssessmentMediaAPIView, AssessmentFeedbackAPIView, CandidateResultAPIView, \
    ProcessOpenEndedAPIView, ResultLIstAPIView, ResultInitializerAPIView

urlpatterns = [
    path('<int:pk>', CandidateResultAPIView.as_view(), name='candidate-result'),
    path('save_answer', SessionAnswerAPIView.as_view(), name='save-session-answer'),
    path('save_session', SessionProcessorAPIView.as_view(), name='save-section'),
    path('save_image', AssessmentImagesAPIView.as_view(), name='save-image'),
    path('save_media', AssessmentMediaAPIView.as_view(), name="save-media"),
    path('save_feedback', AssessmentFeedbackAPIView.as_view(), name="save-feedback"),
    path('process_opa', ProcessOpenEndedAPIView.as_view(), name="process-opa"),
    path('all', ResultLIstAPIView.as_view(), name="result-list"),
    path('init_result', ResultInitializerAPIView.as_view(), name="initial-result")

]
