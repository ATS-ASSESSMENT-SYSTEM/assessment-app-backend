from rest_framework.serializers import ModelSerializer, HyperlinkedIdentityField
from rest_framework import serializers
from assessment.models import Assessment, ApplicationType, AssessmentSession
from questions_category.models import Category


class AssessmentSerializer(ModelSerializer):
    url = HyperlinkedIdentityField(view_name="category-list-view", format='html',)
    
    class Meta:
        model = Assessment
        fields = ("name", "instruction", "application_type", "benchmark", "date_created", "date_updated", "url")
    
    extra_kwargs = {
            'created_date': {'read_only': True},
            'updated_date': {'read_only': True},
    }
    
    def validate(self, attrs):
        assessment_name = attrs.get('name')
        if Assessment.objects.filter(name__iexact=assessment_name).exists():
            raise serializers.ValidationError('Assessment with the same name already exist.')
        return attrs
    
    def validate_benchmark(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError('Benchmark must be between  0 and 100')
        return value
        
    
class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'category_info', 'created_date', 'updated_date')
        extra_kwargs = {
            'created_date': {'read_only': True},
            'updated_date': {'read_only': True},
            'id': {'read_only': True},
        }

class ApplicationTypeSerializer(ModelSerializer):

    class Meta:
        model = ApplicationType
        fields = (
            'title', 'description', 'created_at'
        )

class AssessmentSessionSerializer(ModelSerializer):
    class Meta:
        model = AssessmentSession  
        fields = '__field__'