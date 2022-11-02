from rest_framework  import serializers, HyperlinkedIdentityField
from assessment.models import Assessment

class AssessmentSerializer(serializers.Modelserializer):
    url = HyperlinkedIdentityField(view_name="", format='html',)
    
    class Meta:
        model = Assessment
        fields = ("name", "instruction", "application_type", "date_created", "date_updated", "url")

    
    
    