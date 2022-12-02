from django.test import TestCase

from django.urls import include, path, reverse
from rest_framework import status
from rest_framework.test import APITestCase, URLPatternsTestCase

from questions_category.models import Category, Question


class CategoryTests(APITestCase, URLPatternsTestCase):

    def create_category(self, name, category_info):
        return Category.objects.create(name=name, category_info=category_info)

    urlpatterns = [
        path('api/', include('questions_category.urls')),
    ]

    def test_category_list(self):
        """
        Ensure we can create a new account object.
        """
        url = reverse('questions-category:category-list-create-view')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_category_create(self):
        """
        Ensure we can create a new account object.
        """
        url = reverse('questions-category:category-list-create-view')
        response = self.client.post(url,
                                    data={"name": "DRF8", "category_info": "General questions for all candidates."})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_category_update(self):
        """
        Ensure we can create a new account object.
        """
        create_category = self.create_category(name="DRF", category_info="Category info")
        url = reverse('questions-category:category-retrieve-update-view', args=[create_category.id])
        response = self.client.put(url,
                                   data={"name": "DRF8", "category_info": "General questions for all candidates."})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_category_delete(self):
        """
        Ensure we can create a new account object.
        """
        create_category = self.create_category(name="DRF", category_info="Category info")
        url = reverse('questions-category:category-retrieve-update-view', args=[create_category.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class QuestionTests(APITestCase, URLPatternsTestCase):

    def create_category(self, name, category_info):
        return Category.objects.create(name=name, category_info=category_info)

    def create_question(self, test_category, question_type, question_category, question_text):
        return Question.objects.create(test_category=test_category, question_text=question_text,
                                       question_type=question_type, question_category=question_category)

    urlpatterns = [
        path('api/', include('questions_category.urls')),
    ]

    def test_question_list(self):
        """
        Ensure we can create a new account object.
        """
        create_category = self.create_category(name="Flutter", category_info="category info")
        url = reverse('questions-category:question-list-view', args=[create_category.id])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_question_create(self):
        """
        Ensure we can create a new account object.
        """
        create_category = self.create_category(name="Flutter", category_info="category info")
        url = reverse('questions-category:question-create-view', args=[create_category.id])
        response = self.client.post(url,
                                    data={"question_text": "Question 1", "question_type": "Multi-choice",
                                          "question_category": "Real"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_question_update(self):
        """
        Ensure we can create a new account object.
        """
        create_category = self.create_category(name="Flutter", category_info="Category info")
        create_question = self.create_question(question_text="Question Not Update", question_category="Real",
                                               question_type="Multi-choice", test_category=create_category)
        url = reverse('questions-category:question-retrieve-update-view', args=[create_category.id, create_question.id])
        response = self.client.put(url,
                                   data={"question_text": "Question Update",
                                         "question_type": "Multi-choice", "question_category": "Real"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_question_delete(self):
        """
        Ensure we can create a new account object.
        """
        create_category = self.create_category(name="DRF", category_info="Category info")
        create_question = self.create_question(question_text="Question Delete", question_category="Real",
                                               question_type="Multi-choice", test_category=create_category)
        url = reverse('questions-category:question-retrieve-update-view', args=[create_category.id, create_question.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
