from django.urls import path
from assessment import views

urlpatterns = [
    path('create-list-assessment', views.AssessmentList.as_view(), name='assessment-list-create-view'),
    path('get-assessment-for-candidate', views.GetAssessmentForCandidateAPIView.as_view(), name='get-assessment-for-candidate'),
    path('application-type/', views.ApplicationTypeList.as_view(), name='applicationtype-list-view'),
    path('application-type/<int:pk>', views.ApplicationTypeDetail.as_view(), name='applicationtype-retrieve-view'),
    path('<int:pk>/', views.AssesmentDetail.as_view(), name='assessment-retrieve-update-view'),
    path('<int:pk>/categories', views.CategoryList.as_view(), name='category-list-view'),
    path('<int:assessment_id>/category/<int:id>', views.AddCategoryToAssessmentAPIView.as_view(), name="add-category"),
    path('<int:assessment_id>/categories/<int:category_id>/questions', views.GenerateRandomQuestions.as_view(), name='random-question'),
]
