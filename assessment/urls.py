from django.urls import path
from assessment import views

urlpatterns = [
    path('', views.AssessmentList.as_view(), name='assessment-list-create-view'),
    path('<int:pk>/', views.AssesmentDetail.as_view(), name='assessment-retrieve-update-view'),
    path('<int:pk>/category', views.CategoryList.as_view(), name='category-list-view'),
    path('<int:assessment_id>/category/<int:id>', views.AddCategoryToAssessmentAPIView.as_view(), name="'add-category"),
    
]
