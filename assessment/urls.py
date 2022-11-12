from django.urls import path
from assessment import views

urlpatterns = [
    path('', views.AssessmentList.as_view(), name='assessment-list-create-view'),
    path('application-type/', views.ApplicationTypeList.as_view()),
    path('<int:pk>/', views.AssesmentDetail.as_view(), name='assessment-retrieve-update-view'),
    path('<int:pk>/categories', views.CategoryList.as_view(), name='category-list-view'),
    path('<int:assessment_id>/category/<int:id>', views.AddCategoryToAssessmentAPIView.as_view(), name="'add-category"),
    path('<int:assessment_id>/category/<int:category_id>/questions', views.GenerateRandomQuestions.as_view(), name='random-question'),
]
