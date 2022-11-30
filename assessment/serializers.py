from rest_framework.serializers import ModelSerializer, HyperlinkedIdentityField
from rest_framework import serializers
from assessment.models import Assessment, AssessmentSession
from assessment.models import Assessment, ApplicationType, AssessmentSession

from questions_category.models import Category


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'category_info', 'num_of_questions', 'test_duration', 'created_date', 'updated_date')
        extra_kwargs = {
            'created_date': {'read_only': True},
            'updated_date': {'read_only': True},
            'id': {'read_only': True},
        }


class AssessmentSerializer(ModelSerializer):
    categories = CategorySerializer(many=True, required=False)

    class Meta:
        model = Assessment
        fields = ("id", "name", "assessment_info", "total_duration", "application_type", "benchmark", "date_created",
                  "date_updated", "categories")

    extra_kwargs = {
        'created_date': {'read_only': True},
        'updated_date': {'read_only': True},
    }

    def validate(self, attrs):
        assessment_name = attrs.get('name')
        application_type = attrs.get('application_type')

        if not attrs.get('assessment_info'):
            raise serializers.ValidationError('assessment_info must be provided.')

        if not attrs.get('total_duration'):
            raise serializers.ValidationError('total_duration must be provided.')

        if not attrs.get('benchmark'):
            raise serializers.ValidationError('benchmark must be provided.')

        # if Assessment.objects.filter(name__iexact=assessment_name, application_type=application_type).exists():
        #     raise serializers.ValidationError('Assessment with this name already have the Application type')

        return attrs


class ApplicationTypeSerializer(ModelSerializer):
    class Meta:
        model = ApplicationType
        fields = (
            'id', 'title', 'description', 'uid', 'is_delete'
        )


class StartAssessmentSerializer(serializers.Serializer):
    candidate_id = serializers.CharField()
    device = serializers.CharField()
    browser = serializers.CharField()
    location = serializers.CharField()
    enable_webcam = serializers.BooleanField()
    full_screen_active = serializers.BooleanField()


class GetAssessmentForCandidateSerializer(serializers.Serializer):
    course = serializers.CharField()
