from django.urls import path
from assessment import views

urlpatterns = [
    path('create-list-assessment', views.AssessmentList.as_view(), name='assessment-list-create-view'),
    path('get-assessment-for-candidate', views.GetAssessmentForCandidateAPIView.as_view(), name='get-assessment-for-candidate'),
    path('check-assessment-duration', views.CheckAssessmentDurationAPIView.as_view(), name='check-assessment-duration'),
    path('application-type', views.ApplicationTypeCreate.as_view(), name='applicationtype-create-view'),
    path('application-type/list', views.ApplicationTypeList.as_view(), name='applicationtype-list-view'),
    path('application-type/<uuid:uid>', views.ApplicationTypeDetail.as_view(), name='applicationtype-retrieve-view'),
    path('<int:pk>', views.AssesmentDetail.as_view(), name='assessment-retrieve-update-view'),
    path('<int:assessment_id>/category/<int:id>', views.AddCategoryToAssessmentAPIView.as_view(), name="add-category"),
    path('<int:assessment_id>/categories/<int:category_id>/questions', views.GenerateRandomQuestions.as_view(), name='random-question'),
]
