import json
from abc import ABC

from rest_framework import serializers
from django.db.models import Sum
from django.db.models import Exists

from result.models import Result, Category_Result, Session_Answer
from assessment.models import Assessment, AssessmentSession
from questions_category.models import Category, OpenEndedAnswer


class AssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assessment
        fields = ('name', 'application_type', 'date_created')


class CategoryScoreSerializer(serializers.ModelSerializer):
    name = serializers.CharField()

    class Meta:
        model = Category_Result
        fields = ('name', 'score')


class CandidateSerializer(serializers.Serializer):
    candidate_id = serializers.CharField(max_length=100)
    email = serializers.EmailField()


class ResultSerializer(serializers.ModelSerializer):
    assessment = serializers.CharField(required=True)
    category_score_list = CategoryScoreSerializer(
        many=True, required=True, write_only=True)
    candidate = CandidateSerializer(required=True)

    class Meta:
        model = Result
        fields = ('assessment', 'candidate', 'category_score_list',)

    def validate(self, attrs):

        assessment = attrs.get('assessment')
        candidate = attrs.get('candidate')
        scores = json.loads(json.dumps(attrs.get('category_score_list')))

        category = [category['name'] for category in scores]

        check_assessment = Assessment.objects.filter(name=assessment)

        if not check_assessment.exists():
            raise serializers.ValidationError('Invalid assessment type')

        category_instance = Category.objects.filter(name__in=category)

        if not category_instance.exists():
            raise serializers.ValidationError('Category is invalid')

        # assessment_q = category_instance.filter(assessment__pk=check_assessment.first().pk)
        #
        # if not len(category) is assessment_q.count():
        #     raise serializers.ValidationError('one or more category does not exists in the assessment')

        result_instance = Result.objects.filter(
            assessment=check_assessment.first(), candidate=candidate)

        if result_instance.exists():
            check_category = Category_Result.objects.filter(category__name__in=category,
                                                            result=result_instance.first())
            if check_category.exists():
                raise serializers.ValidationError(
                    'Result category already exists for this candidate')

        return attrs

    def create(self, validated_data):
        # ask:  why am i getting ordered dict

        assessment = Assessment.objects.get(
            name=validated_data.get('assessment'))
        candidate = validated_data.get('candidate')

        scores = json.loads(json.dumps(
            validated_data.pop('category_score_list')))

        create_result, created = Result.objects.get_or_create(assessment=assessment,
                                                              candidate=candidate)
        if create_result:
            for dict_element in scores:
                category_instance = Category.objects.get(
                    name=dict_element['name'])
                if dict_element['multiple_choice_score']:
                    Category_Result.objects.create(
                        result=create_result, score=dict_element['multiple_choice_score'],
                        category=category_instance)

        return create_result


class CandidateResultSerializer(serializers.ModelSerializer):
    result = serializers.SerializerMethodField()
    assessment = AssessmentSerializer()

    class Meta:
        model = Result
        fields = ('assessment', 'candidate', 'created_date')

    def get_result(self, obj):
        # result = {}
        q = Category_Result.objects.filter(result=obj.pk)
        # result['scores'] = q
        # result['total'] = q.aggregate(sum=Sum('score'))
        return q


class CandidatesResultSerializer(serializers.ModelSerializer):
    pass


# class ResultInfoSerializer(serializers.ModelSerializer):
#     assessment = serializers.CharField(required=True)
#     candidate = CandidateSerializer(required=True)
#
#     class Meta:
#         model = Result_Info
#         fields = ('location', 'device', 'enabled_webcam', 'full_screen_active_always', 'images',)

class OpenendedAnswerSerializer(serializers.Serializer):
    question_type = serializers.CharField()
    answer_text = serializers.CharField()


class SessionAnswerSerializer(serializers.ModelSerializer):
    open_ended_info = OpenendedAnswerSerializer(write_only=True)

    class Meta:
        model = Session_Answer
        fields = ('candidate', "assessment", "category", "question", "is_correct", "session",
                  "time_remaining", "open_ended_info")

    def create(self, validated_data):
        is_correct_value = validated_data.pop('is_correct')
        session_remaining_time = validated_data.pop('time_remaining')
        op_info = validated_data.pop('open_ended_info')
        question_type = op_info['question_type']
        answer_text = op_info['answer_text']

        if question_type not in ["Open-ended", 'Multi-choice']:
            raise serializers.ValidationError("Invalid Question Type")

        session_answer = Session_Answer.objects.filter(**validated_data)
        print(session_answer)

        if question_type == "Multi-Choice":
            if session_answer.exists():
                session_answer_instance = session_answer.first()
                session_answer_instance.is_correct = is_correct_value
                session_answer_instance.time_remaining = session_remaining_time
                session_answer_instance.save()
                return session_answer_instance
            new_session_answer = Session_Answer(**validated_data, is_correct=is_correct_value,
                                                time_remaining=session_remaining_time)
            new_session_answer.save()
            return new_session_answer

        if question_type == "Open-ended":
            if session_answer.exists():
                session_answer_instance = session_answer.first()
                session_answer_instance.is_correct = is_correct_value
                session_answer_instance.time_remaining = session_remaining_time
                session_answer_instance.question_type = 'Open-ended'
                session_answer_instance.save()
                OpenEndedAnswer.objects.update_or_create(question=validated_data.get('question'),
                                                         candidate=validated_data.get(
                                                             'candidate'),
                                                         answer_text=answer_text,
                                                         defaults={'question': validated_data.get(
                                                             'question'),
                                                             'candidate': validated_data.get(
                                                                 'candidate')})
                return session_answer_instance
            new_session_answer = Session_Answer(**validated_data, is_correct=is_correct_value,
                                                time_remaining=session_remaining_time, question_type='Open-ended')

            save_op_answer = OpenEndedAnswer(question=validated_data.get('question'),
                                             candidate=validated_data.get('candidate'),
                                             answer_text=answer_text,
                                             )
            new_session_answer.save()
            save_op_answer.save()
            return new_session_answer


class SessionProcessorSerializer(serializers.Serializer):
    session_id = serializers.CharField()

    def validate(self, attrs):
        try:
            session = attrs.get('session_id')

            if session:
                session_instance = AssessmentSession.objects.get(session_id=session)
                session_answers = Session_Answer.objects.filter(
                    session=session_instance).values_list('question', flat=True)
                q_session = session_instance.question_list.all().values_list('id', flat=True)

                if set(session_answers) != set(q_session):
                    raise serializers.ValidationError(
                        'Some questions are yet to be answer, please check and try again')

                result = Result.objects.filter(assessment=session_instance.assessment,
                                               candidate=session_instance.candidate).first()
                print(result)
                if result :
                    section_category = Category_Result.objects.filter(
                        result=result, category=session_instance.category,
                    )
                    if section_category and section_category.exists():
                        raise serializers.ValidationError('This session has already been saved')

                return attrs

            raise serializers.ValidationError('Please Provide a session id')
        except AssessmentSession.DoesNotExist:
            raise serializers.ValidationError('Invalid session id')

    def create(self, validated_data):
        session = validated_data.get('session_id')
        session_instance = AssessmentSession.objects.get(session_id=session)

        result, created = Result.objects.get_or_create(assessment=session_instance.assessment,
                                                       candidate=session_instance.candidate)
        correct_score = Session_Answer.objects.filter(session=session_instance, question_type='Multi-choice',
                                                      is_correct=True).count()
        session_category = Category_Result(result=result, category=session_instance.category, status='TAKEN',
                                           score=correct_score
                                           )
        session_category.save()
        return validated_data
