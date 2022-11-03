from rest_framework import serializers

from assessment.models import Assessment
from .models import Category, Question, Choice


class AssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assessment
        fields = ('name',)


class CategorySerializer(serializers.ModelSerializer):
    questions = serializers.HyperlinkedIdentityField(view_name='question-list-view', format='html')

    class Meta:
        model = Category
        fields = ('id', 'name', 'category_info', 'questions', 'created_date', 'updated_date')
        extra_kwargs = {
            'created_date': {'read_only': True},
            'updated_date': {'read_only': True},
            'id': {'read_only': True},
        }


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ('choice_text', 'is_correct')


class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, required=False)

    def validate(self, attrs):
        print(attrs)
        choice = attrs.get('choices')
        if not choice:
            raise serializers.ValidationError('Question must have at least 2 choices')

        if len(attrs['choices']) < 2:
            raise serializers.ValidationError('Choices must be 2 at least')

        return attrs

    class Meta:
        model = Question
        fields = ('question_text', 'question_type', 'difficult', 'choices')

    def create(self, validated_data):
        try:
            category_pk = self.context['request'].parser_context.get('kwargs').get('pk')
            category = Category.objects.get(pk=category_pk)
            choices = validated_data.pop('choices')
            obj = Question.objects.create(test_category=category, question_type=validated_data['question_type'],
                                          question_text=validated_data['question_text'],
                                          difficult=validated_data['difficult'])
            for choice in choices:
                c = Choice.objects.create(question=obj, **choice)
                print(c)
            return obj
        except Category.DoesNotExist:
            return None
