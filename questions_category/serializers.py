from rest_framework import serializers

from assessment.models import Assessment
from result.models import Session_Answer
from .models import Category, Question, Choice, OpenEndedAnswer


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
        fields = ('id', 'question_text', 'question_type', 'question_category', 'choices')

    def validate(self, attrs):
        choices = attrs.get('choices')
        category_pk = self.context['request'].parser_context.get('kwargs').get('pk')
        question_type = attrs.get('question_type')
        question_category = attrs.get('question_category')

        if not question_type:
            raise serializers.ValidationError('question_type must be provided.')

        if not question_category:
            raise serializers.ValidationError('question_category must be provided.')

        if question_type == 'Multi-choice':
            if not choices:
                raise serializers.ValidationError('choices field must be provided.')

            if len(choices) < 2:
                raise serializers.ValidationError('Choices must be 2 at least')

        if question_type == 'Multi-response':
            if not choices:
                raise serializers.ValidationError('choices field must be provided.')

            if len(choices) < 3:
                raise serializers.ValidationError('Choices must be 3 at least')

        if question_type == 'Open-ended':
            if choices:
                raise serializers.ValidationError('Open ended question have no choices')

        if Question.active_objects.filter(question_text__iexact=attrs.get('question_text'),
                                   test_category__pk=category_pk).exists():
            raise serializers.ValidationError('The question already exist in the category.')

        return attrs

    def create(self, validated_data):
        try:
            category_pk = self.context['request'].parser_context.get(
                'kwargs').get('pk')
            category = Category.active_objects.get(pk=category_pk)
            choices = validated_data.get('choices')
            if choices:
                validated_data.pop('choices')
                obj = Question.objects.create(test_category=category, **validated_data)
                for choice in choices:
                    Choice.objects.create(question=obj, **choice)
                return obj
            obj = Question.objects.create(test_category=category, **validated_data)

            return obj
        except Category.DoesNotExist:
            raise serializers.ValidationError('The category is not known')

    def update(self, instance, validated_data):
        choices = validated_data.get('choices')
        question_type = validated_data.get('question_type')
        question_text = validated_data.get('question_text')
        category_pk = self.context['request'].parser_context.get('kwargs').get('test_category_id')

        if Question.active_objects.filter(question_text__iexact=question_text,
                                   test_category__pk=category_pk).exists():
            raise serializers.ValidationError('The question already exist in the category.')

        if question_type == 'Open-ended':
            if instance.question_type == 'Multi-choice' or instance.question_type == 'Multi-response':
                raise serializers.ValidationError("You can't swap the question type.")

        if question_type == 'Multi-choice':
            if instance.question_type == 'Open-ended' or instance.question_type == 'Multi-response':
                raise serializers.ValidationError("You can't swap the question type.")

        if question_type == 'Multi-response':
            if instance.question_type == 'Open-ended' or instance.question_type == 'Multi-choice':
                raise serializers.ValidationError("You can't swap the question type.")

        if choices:
            validated_data.pop('choices')
        return super().update(instance, validated_data)


class OpenEndedAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpenEndedAnswer
        fields = ('answer_text',)


class GenerateQuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, required=False)
    session_answer = SessionAnswerSerializer(many=True, required=False)
    open_ended_answer_text = OpenEndedAnswerSerializer(many=True, required=False)

    class Meta:
        model = Question
        fields = ('id', 'question_text', 'question_type', 'question_category', 'choices',
                  'session_answer', 'open_ended_answer_text')


class CategorySerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, required=False)

    class Meta:
        model = Category
        fields = (
        'id', 'name', 'category_info', 'num_of_questions', 'test_duration', 'created_date', 'updated_date', 'questions')

        extra_kwargs = {
            'created_date': {'read_only': True},
            'updated_date': {'read_only': True},
            'id': {'read_only': True},
        }

    def validate(self, attrs):
        category_name = attrs.get('name')
        if Category.active_objects.filter(name__iexact=category_name).exists():
            raise serializers.ValidationError('Category with the same name already exist.')

        return attrs
