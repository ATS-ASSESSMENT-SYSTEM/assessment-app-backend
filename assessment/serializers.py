from rest_framework.serializers import ModelSerializer, HyperlinkedIdentityField
from assessment.models import Assessment
from questions_category.models import Category

class AssessmentSerializer(ModelSerializer):
    url = HyperlinkedIdentityField(view_name="category-list-view", format='html',)
    
    class Meta:
        model = Assessment
        fields = ("name", "instruction", "application_type", "date_created", "date_updated", "url")
    
    extra_kwargs = {
            'created_date': {'read_only': True},
            'updated_date': {'read_only': True},
    }
    
class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'category_info', 'questions', 'created_date', 'updated_date')
        extra_kwargs = {
            'created_date': {'read_only': True},
            'updated_date': {'read_only': True},
            'id': {'read_only': True},
        }
    