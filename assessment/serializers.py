from rest_framework  import serializers
from assessment.models import Assessment

class AssessmentSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200, null=True)
    application_type = serializers.CharField(max_length=200, null=True)
    date_created = serializers.models.DateField(auto_now_add=True)
    date_updated = serializers.models.DateField(auto_now=True)
    is_delete = serializers.models.BooleanField(default=False)