import json
from abc import ABC

from rest_framework import serializers
from django.db.models import Sum, Q

from result.models import Result, Category_Result, Session_Answer, AssessmentImages, \
    AssessmentMedia, AssessmentFeedback
from assessment.models import Assessment, AssessmentSession
from questions_category.models import Category, OpenEndedAnswer, Question, Choice


# class CandidateSerializer(serializers.Serializer):
#     candidate_id = serializers.CharField(max_length=100)
#     email = serializers.EmailField()


# class ResultSerializer(serializers.ModelSerializer):
#     assessment = serializers.CharField(required=True)
#     category_score_list = CategoryScoreSerializer(
#         many=True, required=True, write_only=True)
#     candidate = CandidateSerializer(required=True)
#
#     class Meta:
#         model = Result
#         fields = ('assessment', 'candidate', 'category_score_list',)
#
#     def validate(self, attrs):
#
#         assessment = attrs.get('assessment')
#         candidate = attrs.get('candidate')
#         scores = json.loads(json.dumps(attrs.get('category_score_list')))
#
#         category = [category['name'] for category in scores]
#
#         check_assessment = Assessment.objects.filter(name=assessment)
#
#         if not check_assessment.exists():
#             raise serializers.ValidationError('Invalid assessment type')
#
#         category_instance = Category.objects.filter(name__in=category)
#
#         if not category_instance.exists():
#             raise serializers.ValidationError('Category is invalid')
#
#         # assessment_q = category_instance.filter(assessment__pk=check_assessment.first().pk)
#         #
#         # if not len(category) is assessment_q.count():
#         #     raise serializers.ValidationError('one or more category does not exists in the assessment')
#
#         result_instance = Result.objects.filter(
#             assessment=check_assessment.first(), candidate=candidate)
#
#         if result_instance.exists():
#             check_category = Category_Result.objects.filter(category__name__in=category,
#                                                             result=result_instance.first())
#             if check_category.exists():
#                 raise serializers.ValidationError(
#                     'Result category already exists for this candidate')
#
#         return attrs
#
#     def create(self, validated_data):
#         # ask:  why am I getting ordered dict
#
#         assessment = Assessment.objects.get(
#             name=validated_data.get('assessment'))
#         candidate = validated_data.get('candidate')
#
#         scores = json.loads(json.dumps(
#             validated_data.pop('category_score_list')))
#
#         create_result, created = Result.objects.get_or_create(assessment=assessment,
#                                                               candidate=candidate)
#         if create_result:
#             for dict_element in scores:
#                 category_instance = Category.objects.get(
#                     name=dict_element['name'])
#                 if dict_element['multiple_choice_score']:
#                     Category_Result.objects.create(
#                         result=create_result, score=dict_element['multiple_choice_score'],
#                         category=category_instance)
#
#         return create_result


class SessionAnswerSerializer(serializers.ModelSerializer):
    answer_text = serializers.CharField(required=False)
    question_type = serializers.CharField()
    mr_answers = serializers.ListSerializer(
        child=serializers.IntegerField(), required=False
    )

    class Meta:
        model = Session_Answer
        fields = ('candidate', "assessment", "category", "question", "is_correct", "session",
                  "time_remaining", "question_type", "choice", "answer_text", "mr_answers")
        extra_kwargs = {"answer_text": {"required": False, "allow_null": True}}

    def validate(self, attrs):
        try:
            print("attribute=>", attrs)
            session = attrs.get('session')

            question_type = attrs.get('question_type')

            if question_type not in ["Open-ended", 'Multi-choice', 'Multi-response']:
                raise serializers.ValidationError("Invalid Question Type")

            if question_type == 'Multi-choice' and attrs.get('answer_text'):
                attrs.pop('answer_text')

            if question_type == 'Multi-response':
                mr_answers = attrs.get('mr_answers')
                if not mr_answers:
                    raise serializers.ValidationError('Please select answers for the question')

            if question_type == 'Open-ended':
                answer_text = attrs.get('answer_text')
                if not answer_text:
                    raise serializers.ValidationError('Please provide an answer for the question')

            check_session = AssessmentSession.objects.get(session_id=session.session_id)
            check_question = Question.objects.filter(pk=attrs['question'].pk).first()
            print(check_question.question_type, question_type)
            if check_question.question_type != question_type:
                raise serializers.ValidationError('Question type does not match the question ')

            if check_session.assessment != attrs.get('assessment'):
                raise serializers.ValidationError('Invalid assessment ID')

            if attrs.get('question_type') == 'Open-ended' and not attrs.get('answer_text'):
                raise serializers.ValidationError('Please, provide an answer for the question')

            return attrs
        except AssessmentSession.DoesNotExist:
            raise serializers.ValidationError('Invalid Session ID')

    def create(self, validated_data):
        print("validate=>", validated_data)
        try:
            session_remaining_time = validated_data.pop('time_remaining')
            if validated_data.get('is_correct'):
                is_correct_value = validated_data.pop('is_correct')
            question_type = validated_data.pop('question_type')

            if question_type == 'Open-ended':
                answer_text = validated_data.pop('answer_text')

            if question_type == 'Multi-response':
                mr_answers = validated_data.pop('mr_answers')

            session = validated_data.get("session")
            choice = validated_data.get("choice")
            print(session, validated_data)

            session_answer = Session_Answer.objects.filter(**validated_data)

            if session_answer.exists():
                if session_answer.first().question_type != question_type:
                    raise serializers.ValidationError("You can't interchange question type")

            if question_type == "Multi-response":
                check_mr_answers = Choice.objects.filter(id__in=mr_answers) \
                    .exclude(is_correct=True)
                if check_mr_answers.count() > 0:
                    all_correct = False
                else:
                    all_correct = True

                if session_answer.exists():
                    session_answer_instance = session_answer.first()
                    session_answer_instance.is_correct = all_correct
                    session_answer_instance.time_remaining = session_remaining_time
                    session_answer_instance.question_type = question_type
                    session_answer_instance.save()

                    return session_answer_instance
                new_session_answer = Session_Answer(**validated_data, is_correct=all_correct,
                                                    time_remaining=session_remaining_time,
                                                    mr_answers_id=mr_answers
                                                    )
                new_session_answer.save()
                return new_session_answer

            if question_type == "Multi-choice":
                if session_answer.exists():
                    session_answer_instance = session_answer.first()
                    session_answer_instance.is_correct = is_correct_value
                    session_answer_instance.time_remaining = session_remaining_time
                    session_answer_instance.choice = choice
                    session_answer_instance.question_type = 'Multi-choice'
                    session_answer_instance.save()
                    return session_answer_instance
                new_session_answer = Session_Answer(**validated_data, is_correct=is_correct_value,
                                                    time_remaining=session_remaining_time)
                new_session_answer.save()
                return new_session_answer

            if question_type == "Open-ended":

                if session_answer.exists():
                    session_answer_instance = session_answer.first()
                    session_answer_instance.time_remaining = session_remaining_time
                    session_answer_instance.question_type = 'Open-ended'
                    session_answer_instance.save()
                    OpenEndedAnswer.objects.filter(question=validated_data.get('question'),
                                                   candidate=validated_data.get(
                                                       'candidate'),
                                                   category=validated_data.get('category'),
                                                   ).update(answer_text=answer_text)
                    return session_answer_instance
                new_session_answer = Session_Answer(**validated_data,
                                                    time_remaining=session_remaining_time, question_type='Open-ended', )

                save_op_answer = OpenEndedAnswer(question=validated_data.get('question'),
                                                 candidate=validated_data.get('candidate'),
                                                 answer_text=answer_text,
                                                 category=validated_data.get('category')
                                                 )
                new_session_answer.save()
                save_op_answer.save()
                return new_session_answer

            raise serializers.ValidationError('Invalid data provided, please confirm and check again')
        except KeyError as error:
            raise serializers.ValidationError(f'Some field were not provided:{error}')


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
                print(session_answers, q_session)
                if set(session_answers) != set(q_session):
                    raise serializers.ValidationError(
                        'Some questions are yet to be answer, please check and try again')

                result = Result.objects.filter(assessment=session_instance.assessment,
                                               candidate=session_instance.candidate_id).first()
                print(result)
                if result:
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
                                                       candidate=session_instance.candidate_id, )
        correct_score = Session_Answer.objects.filter(Q(question_type='Multi-choice') |
                                                      Q(question_type='Multi-response'),
                                                      session=session_instance, is_correct=True, )

        has_open_ended_answer = OpenEndedAnswer.objects.filter(candidate=session_instance.candidate_id,
                                                               category=session_instance.category)
        if has_open_ended_answer.count() > 0:
            has_open_ended_answer = True

        session_category = Category_Result(result=result, category=session_instance.category,
                                           score=correct_score.count(),
                                           has_open_ended=has_open_ended_answer
                                           )
        session_category.save()
        # correct_score.delete()
        # session_instance.delete()

        return validated_data


# class SessionSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = AssessmentSession
#         field = ('session_id',)


class AssessmentImageSerializer(serializers.ModelSerializer):
    session_id = serializers.CharField(write_only=True)

    class Meta:
        model = AssessmentImages
        fields = ('image', 'session_id')

    def validate(self, attrs):
        print(attrs)
        try:
            AssessmentSession.objects.get(session_id=attrs.get('session_id'))
            return attrs
        except AssessmentSession.DoesNotExist:
            raise serializers.ValidationError("Invalid Session ID")


class ApplicantSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    candidate_id = serializers.CharField(max_length=100)
    email = serializers.CharField(max_length=100)


class ResultListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        field = ['candidate', 'status', 'created_date', 'is_active']


class AssessmentMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentMedia
        fields = ('assessment', 'media_type', 'candidate', 'media')

    def validate(self, attrs):
        media_type = attrs.get('media_type')
        if media_type not in ['Sound', 'Video', 'Image'] or media_type is None:
            raise serializers.ValidationError('Invalid  Media type, can only be Sound, Video or Image')
        return attrs


class AssessmentFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentFeedback
        fields = ('assessment', 'applicant_info', 'feedback')

    def validate(self, attrs):
        q = AssessmentFeedback.objects.filter(assessment=attrs['assessment'],
                                              applicant_info=attrs['applicant_info'])
        if q.exists():
            raise serializers.ValidationError('You already gave a feedback for the assessment')

        return attrs


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ('question_text',)


class OpenEndedSerializer(serializers.ModelSerializer):
    question = QuestionSerializer()

    class Meta:
        model = OpenEndedAnswer
        fields = ('id', "is_correct", "question", "answer_text", "is_marked", "category")


class CandidateCategoryResultSerializer(serializers.ModelSerializer):
    no_of_questions = serializers.SerializerMethodField()
    percentage_mark = serializers.SerializerMethodField()
    open_ended_questions = serializers.SerializerMethodField()
    feedback = serializers.SerializerMethodField()

    class Meta:
        model = Category_Result
        fields = ('category', 'score', 'status', 'no_of_questions', 'percentage_mark',
                  'open_ended_questions', 'feedback')

    def get_no_of_questions(self, objs):
        return Question.objects.filter(test_category_id=objs.category.pk).count()

    def get_percentage_mark(self, objs):
        print("division=>0", objs.score, self.get_no_of_questions(objs))
        return (objs.score / self.get_no_of_questions(objs)) * 100

    def get_open_ended_questions(self, objs):
        opa_answer = OpenEndedAnswer.objects.filter(candidate=objs.result.candidate, category=objs.category)
        return OpenEndedSerializer(opa_answer, many=True).data

    def get_feedback(self, objs):
        fb = AssessmentFeedback.objects.filter(applicant_info__applicantId=objs.result.candidate,
                                               assessment=objs.result.assessment)
        return AssessmentFeedbackSerializer(fb.first()).data


class CandidateResultSerializer(serializers.ModelSerializer):
    category_info = CandidateCategoryResultSerializer(many=True)


    class Meta:
        model = Result
        fields = (
            'candidate', 'is_active', 'result_status', 'duration', 'result_total', 'applicant_info',
            'images', 'category_info')
        extra_kwargs = {'category_info': {'read_only': True},

                        }



class ProcessOpenEndedAnswerSerializer(serializers.Serializer):
    result_id = serializers.IntegerField()
    opa_pk = serializers.IntegerField()
    is_correct = serializers.BooleanField()
    category = serializers.IntegerField()

    def validate(self, attrs):
        try:
            Result.objects.get(pk=attrs['result_id'])
            Category.objects.get(pk=attrs['category'])

        except (Result.DoesNotExist, Category.DoesNotExist) as e:
            raise serializers.ValidationError(e)
        return attrs

    def create(self, validated_data):
        try:
            opa_answer = OpenEndedAnswer.objects.get(pk=validated_data.get('opa_pk'))
            print(opa_answer)
            if opa_answer.is_marked:
                q = Category_Result.objects.get(result_id=validated_data.get('result_id'),
                                                category=validated_data.get('category'))
                if validated_data.get('is_correct') and not opa_answer.is_correct:
                    q.score += 1
                    q.save()
                    return validated_data
                if not validated_data.get('is_correct') and opa_answer:
                    q.score -= 1
                    q.save()
                    return validated_data
            opa_answer.is_correct = validated_data.get('is_correct')
            opa_answer.is_marked = True
            opa_answer.save()
            if validated_data.get('is_correct'):
                q = Category_Result.objects.get(result_id=validated_data.get('result_id'),
                                                category=validated_data.get('category'))
                q.score += 1
                q.save()

            return validated_data

        except OpenEndedAnswer.DoesNotExist:
            raise serializers.ValidationError('Invalid Data Provided')
