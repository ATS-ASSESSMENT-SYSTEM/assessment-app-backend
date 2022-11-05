from django.urls import path

from .views import AddResultAPIView

urlpatterns = [
    path('create', AddResultAPIView.as_view(), name='add-result')
]
