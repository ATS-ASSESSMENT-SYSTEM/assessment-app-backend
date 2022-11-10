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
        fields = ('id', 'name', 'category_info', 'questions', 'test_duration', 'created_date', 'updated_date')
        extra_kwargs = {
            'created_date': {'read_only': True},
            'updated_date': {'read_only': True},
            'id': {'read_only': True},
        }

    def validate(self, attrs):
        category_name = attrs.get('name')
        if Category.objects.filter(name__iexact=category_name).exists():
            raise serializers.ValidationError('Category with the same name already exist.')

        return attrs


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ('id', 'choice_text', 'is_correct')


class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, required=False)

    class Meta:
        model = Question
        fields = ('id', 'question_text', 'question_type', 'difficult', 'question_categories', 'choices')

    def validate(self, attrs):
        choices = attrs.get('choices')
        category_pk = self.context['request'].parser_context.get('kwargs').get('pk')

        if attrs['question_type'] == 'Multi-choices':
            if not choices:
                raise serializers.ValidationError('Question must have at least 2 choices')

            if len(choices) < 2:
                raise serializers.ValidationError('Choices must be 2 at least')

        if attrs['question_type'] == 'Open-ended':
            if choices:
                raise serializers.ValidationError('Open ended question have no choices')

        if Question.objects.filter(question_text=attrs['question_text'], test_category__pk=category_pk).exists():
            raise serializers.ValidationError('The question already exist in the category.')

        return attrs

    def create(self, validated_data):
        try:
            category_pk = self.context['request'].parser_context.get('kwargs').get('pk')
            category = Category.objects.get(pk=category_pk)
            choices = validated_data.get('choices')
            if choices:
                obj = Question.objects.create(test_category=category, question_type=validated_data['question_type'],
                                              question_categories=validated_data['question_categories'],
                                              question_text=validated_data['question_text'],
                                              difficult=validated_data['difficult'])
                for choice in choices:
                    Choice.objects.create(question=obj, **choice)
                return obj
            obj = Question.objects.create(test_category=category, question_type=validated_data['question_type'],
                                          question_categories=validated_data['question_categories'],
                                          question_text=validated_data['question_text'],
                                          difficult=validated_data['difficult'])

            return obj
        except Category.DoesNotExist:
            raise serializers.ValidationError('The category is not known')

    def update(self, instance, validated_data):
        category_pk = self.context['request'].parser_context.get('kwargs').get('test_category_id')
        category = Category.objects.get(pk=category_pk)
        choices = validated_data.pop('choices')
        instance.test_category = category
        instance.question_text = validated_data['question_text']
        instance.question_type = validated_data['question_type']
        instance.question_categories = validated_data['question_categories']
        instance.difficult = validated_data['difficult']
        instance.save()
        return instance

