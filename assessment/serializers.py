from rest_framework.serializers import ModelSerializer, HyperlinkedIdentityField
from rest_framework import serializers
from assessment.models import Assessment, AssessmentSession
from assessment.models import Assessment, ApplicationType, AssessmentSession

from questions_category.models import Category


class AssessmentSerializer(ModelSerializer):
    categories = HyperlinkedIdentityField(view_name="category-list-view", format='html', )
    
    class Meta:
        model = Assessment
        fields = ("name", "instruction", "application_type", "benchmark", "date_created", "date_updated", "categories")
        
    extra_kwargs = {
        'created_date': {'read_only': True},
        'updated_date': {'read_only': True},
    }
    
    def validate(self, attrs):
        assessment_name = attrs.get('name')
        if Assessment.objects.filter(name__iexact=assessment_name).exists():
            raise serializers.ValidationError('Assessment with the same name already exist.')

        if not attrs.get('instruction'):
            raise serializers.ValidationError('You must provide instruction for an assessment.')

        return attrs
    
    def validate_benchmark(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError('Benchmark must be between  0 and 100')
        
        return value
    
    
class CategorySerializer(ModelSerializer):
    questions = serializers.HyperlinkedIdentityField(view_name='question-list-view', format='html')
    
    class Meta:
        model = Category
        fields = ('id', 'name', 'category_info', 'questions', 'created_date', 'updated_date')
        extra_kwargs = {
            'created_date': {'read_only': True},
            'updated_date': {'read_only': True},
            'id': {'read_only': True},
        }
        
        
class ApplicationTypeSerializer(ModelSerializer):
    class Meta:
        model = ApplicationType
        fields = (
            'title', 'description'
        )
        
        
class StartAssessmentSerializer(serializers.Serializer):
    applicant_id = serializers.CharField()
    device = serializers.CharField()
    browser = serializers.CharField()
    location = serializers.CharField()
    enable_webcam = serializers.BooleanField()
    full_screen_active = serializers.BooleanField()

