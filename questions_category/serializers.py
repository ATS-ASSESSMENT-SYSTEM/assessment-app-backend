from rest_framework import serializers

from assessment.models import Assessment
from result.models import Session_Answer
from .models import Category, Question, Choice


class AssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assessment
        fields = ('name',)


class CategorySerializer(serializers.ModelSerializer):
    questions = serializers.HyperlinkedIdentityField(
        view_name='question-list-view', format='html')

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
        
        
class SessionAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session_Answer
        fields = ('choice', 'time_remaining')


class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, required=False)

    class Meta:
        model = Question
        fields = ('id', 'question_text', 'question_type', 'question_category', 'question_hint', 'choices')

    def validate(self, attrs):
        choices = attrs.get('choices')
        category_pk = self.context['request'].parser_context.get('kwargs').get('pk')
        question_hint = attrs.get('question_hint')
        question_type = attrs.get('question_type')
        question_category = attrs.get('question_category')

        if not question_type:
            raise serializers.ValidationError('question_type must be provided.')

        if not question_category:
            raise serializers.ValidationError('question_category must be provided.')

        if not question_hint:
            raise serializers.ValidationError('question_hint must be provided.')

        if question_type == 'Multi-choice':
            if not choices:
                raise serializers.ValidationError('choices must be provided.')

            if len(choices) < 2:
                raise serializers.ValidationError('Choices must be 2 at least')

        if question_type == 'Open-ended':
            if choices:
                raise serializers.ValidationError('Open ended question have no choices')

        if Question.objects.filter(question_text__iexact=attrs.get('question_text'),
                                   test_category__pk=category_pk).exists():
            raise serializers.ValidationError('The question already exist in the category.')

        return attrs

    def create(self, validated_data):
        try:
            category_pk = self.context['request'].parser_context.get(
                'kwargs').get('pk')
            category = Category.objects.get(pk=category_pk)
            choices = validated_data.get('choices')
            if choices:
                obj = Question.objects.create(test_category=category, question_type=validated_data['question_type'],
                                              question_category=validated_data['question_category'],
                                              question_text=validated_data['question_text'],
                                              question_hint=validated_data['question_hint'])
                for choice in choices:
                    Choice.objects.create(question=obj, **choice)
                return obj
            obj = Question.objects.create(test_category=category, question_type=validated_data['question_type'],
                                          question_category=validated_data['question_category'],
                                          question_text=validated_data['question_text'],
                                          question_hint=validated_data['question_hint'])

            return obj
        except Category.DoesNotExist:
            raise serializers.ValidationError('The category is not known')

    def update(self, instance, validated_data):
        choices = validated_data.get('choices')
        if choices:
            validated_data.pop('choices')
        return super().update(instance, validated_data)
    

class GenerateQuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, required=False)
    session_answer = SessionAnswerSerializer(many=True, required=False)

    class Meta:
        model = Question
        fields = ('id', 'question_text', 'question_type', 'question_category', 'question_hint', 'choices',
                  'session_answer')