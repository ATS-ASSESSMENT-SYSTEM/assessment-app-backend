from django.utils import timezone
from rest_framework import serializers
from django.db.models import Sum, Q

from result.models import Result, CategoryResult, SessionAnswer, AssessmentImages, \
    AssessmentMedia, AssessmentFeedback
from assessment.models import Assessment, AssessmentSession, ApplicationType
from questions_category.models import Category, OpenEndedAnswer, Question, Choice


class SessionAnswerSerializer(serializers.ModelSerializer):
    answer_text = serializers.CharField(required=False)
    question_type = serializers.CharField()
    mr_answers = serializers.ListSerializer(
        child=serializers.IntegerField(), required=False
    )

    class Meta:
        model = SessionAnswer
        fields = ('candidate', "assessment", "category", "question", "is_correct", "session",
                  "time_remaining", "question_type", "choice", "answer_text", "mr_answers")
        extra_kwargs = {"answer_text": {"required": False, "allow_null": True}}

    def validate(self, attrs):
        try:
            print("attribute=>", attrs)
            session = attrs.get('session')
            assessment = attrs.get('assessment')

            question_type = attrs.get('question_type')

            if question_type not in ["Open-ended", 'Multi-choice', 'Multi-response']:
                raise serializers.ValidationError("Invalid Question Type")

            if question_type == 'Multi-choice' and attrs.get('answer_text'):
                attrs.pop('answer_text')

            check_session = AssessmentSession.active_objects.filter(assessment=assessment,
                                                                    candidate_id=attrs.get(
                                                                        'candidate')).order_by(
                'date_created')

            if check_session.exists():
<<<<<<< HEAD
                if ((timezone.now() - check_session.first().date_created).total_seconds() / 3600) \
                        > assessment.total_duration:
                    raise serializers.ValidationError("Your assessment session has expired.")
=======
                if ((
                        timezone.now() - check_session.first().date_created).total_seconds() / 3600) > assessment.total_duration:
                    raise serializers.ValidationError(
                        "Your assessment session has expired.")
>>>>>>> 73a479f8115b52b0248ef5d6268c82d08c968a57

            if question_type == 'Multi-response':
                mr_answers = attrs.get('mr_answers')
                if not mr_answers:
                    raise serializers.ValidationError(
                        'Please select answers for the question')

            if question_type == 'Open-ended':
                answer_text = attrs.get('answer_text')
                if not answer_text:
                    raise serializers.ValidationError(
                        'Please provide an answer for the question')

            check_session = AssessmentSession.objects.get(
                session_id=session.session_id)
            check_question = Question.objects.filter(
                pk=attrs['question'].pk).first()

            if check_session.candidate_id != attrs.get('candidate'):
                raise serializers.ValidationError(
                    'This session is already active for another candidate')

            print(check_question.question_type, question_type)

            if check_question.question_type != question_type:
                raise serializers.ValidationError(
                    'Question type does not match the question ')

            if check_session.assessment != attrs.get('assessment'):
                raise serializers.ValidationError('Invalid assessment ID')

            if attrs.get('question_type') == 'Open-ended' and not attrs.get('answer_text'):
                raise serializers.ValidationError(
                    'Please, provide an answer for the question')

            return attrs
        except AssessmentSession.DoesNotExist:
            raise serializers.ValidationError('Invalid Session ID')

    def create(self, validated_data):
        print("validate=>", validated_data)
        try:
            session_remaining_time = validated_data.pop('time_remaining')

            question_type = validated_data.pop('question_type')

            if question_type == 'Open-ended':
                answer_text = validated_data.pop('answer_text')

            if question_type == 'Multi-response':
                mr_answers = validated_data.pop('mr_answers')

            session = validated_data.get("session")
            choice = validated_data.get("choice")
            print(session, validated_data)

            SessionAnswer = SessionAnswer.objects.filter(**validated_data)

            if SessionAnswer.exists():
                if SessionAnswer.first().question_type != question_type:
                    raise serializers.ValidationError(
                        "You can't interchange question type")

            if question_type == "Multi-response":
                check_mr_answers = Choice.objects.filter(id__in=mr_answers) \
                    .exclude(is_correct=True)
                if check_mr_answers.count() > 0:
                    all_correct = False
                else:
                    all_correct = True

                if SessionAnswer.exists():
                    SessionAnswer_instance = SessionAnswer.first()
                    SessionAnswer_instance.is_correct = all_correct
                    SessionAnswer_instance.time_remaining = session_remaining_time
                    SessionAnswer_instance.question_type = question_type
                    SessionAnswer_instance.save()

                    return SessionAnswer_instance
                new_SessionAnswer = SessionAnswer(**validated_data, is_correct=all_correct,
                                                  time_remaining=session_remaining_time,
                                                  mr_answers_id=mr_answers
                                                  )
                new_SessionAnswer.save()
                return new_SessionAnswer

            if question_type == "Multi-choice":

                is_correct_value = validated_data.pop('is_correct')
                if SessionAnswer.exists():
                    SessionAnswer_instance = SessionAnswer.first()
                    SessionAnswer_instance.is_correct = is_correct_value
                    SessionAnswer_instance.time_remaining = session_remaining_time
                    SessionAnswer_instance.choice = choice
                    SessionAnswer_instance.question_type = 'Multi-choice'
                    SessionAnswer_instance.save()
                    return SessionAnswer_instance
                new_SessionAnswer = SessionAnswer(**validated_data, is_correct=is_correct_value,
                                                  time_remaining=session_remaining_time)
                new_SessionAnswer.save()
                return new_SessionAnswer

            if question_type == "Open-ended":

                if SessionAnswer.exists():
                    SessionAnswer_instance = SessionAnswer.first()
                    SessionAnswer_instance.time_remaining = session_remaining_time
                    SessionAnswer_instance.question_type = 'Open-ended'
                    SessionAnswer_instance.save()
                    OpenEndedAnswer.objects.filter(question=validated_data.get('question'),
                                                   candidate=validated_data.get(
                                                       'candidate'),
                                                   category=validated_data.get(
                                                       'category'),
                                                   ).update(answer_text=answer_text)
                    return SessionAnswer_instance
                new_SessionAnswer = SessionAnswer(**validated_data,
                                                  time_remaining=session_remaining_time, question_type='Open-ended', )

                save_op_answer = OpenEndedAnswer(question=validated_data.get('question'),
                                                 candidate=validated_data.get(
                                                     'candidate'),
                                                 answer_text=answer_text,
                                                 category=validated_data.get(
                                                     'category')
                                                 )
                new_SessionAnswer.save()
                save_op_answer.save()
                return new_SessionAnswer

            raise serializers.ValidationError(
                'Invalid data provided, please confirm and check again')
        except KeyError as error:
            raise serializers.ValidationError(
                f'Some field were not provided:{error}')


class SessionProcessorSerializer(serializers.Serializer):
    session_id = serializers.CharField()

    def validate(self, attrs):
        try:
            session = attrs.get('session_id')

            if session:
                session_instance = AssessmentSession.objects.get(
                    session_id=session)

                SessionAnswers = SessionAnswer.objects.filter(
                    session=session_instance).values_list('question', flat=True)

                q_session = session_instance.question_list.all().values_list('id', flat=True)

                print(SessionAnswers, q_session)

                if set(SessionAnswers) != set(q_session):
                    raise serializers.ValidationError(
                        'Some questions are yet to be answer, please check and try again')

                result = Result.objects.filter(assessment=session_instance.assessment,
                                               candidate=session_instance.candidate_id).first()
                print(result)
                if result:
                    section_category = CategoryResult.objects.filter(
                        result=result, category=session_instance.category,
                    )
                    if section_category and section_category.exissts():
                        raise serializers.ValidationError(
                            'This session has already been saved')

                return attrs

            raise serializers.ValidationError('Please Provide a session id')
        except AssessmentSession.DoesNotExist:
            raise serializers.ValidationError('Invalid session id')

    def create(self, validated_data):
        session = validated_data.get('session_id')

        session_instance = AssessmentSession.objects.get(session_id=session)

        result, created = Result.objects.get_or_create(assessment=session_instance.assessment,
                                                       candidate=session_instance.candidate_id, )

        correct_score = SessionAnswer.objects.filter(Q(question_type='Multi-choice') |
                                                     Q(question_type='Multi-response'),
                                                     session_id=session, is_correct=True)
        has_open_ended_answer = OpenEndedAnswer.objects.filter(candidate=session_instance.candidate_id,
                                                               category=session_instance.category)

        has_open_ended = bool(has_open_ended_answer.count())

        session_category = CategoryResult.objects.create(result_id=result.pk, category=session_instance.category,
                                                         score=correct_score.count(),
                                                         has_open_ended=has_open_ended,
                                                         status='FINISHED'
                                                         )
        session_category.save()
<<<<<<< HEAD

=======
>>>>>>> 73a479f8115b52b0248ef5d6268c82d08c968a57
        return validated_data


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


class AssessmentMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentMedia
        fields = ('assessment', 'media_type', 'candidate', 'media')

    def validate(self, attrs):
        media_type = attrs.get('media_type')
        if media_type not in ['Sound', 'Video', 'Image'] or media_type is None:
            raise serializers.ValidationError(
                'Invalid  Media type, can only be Sound, Video or Image')
        return attrs


class ApplicationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationType
        fields = ('title',)


class AssessmentSerializer(serializers.ModelSerializer):
    application_type = ApplicationTypeSerializer(read_only=True)

    class Meta:
        model = Assessment
        fields = (
            'assessment_info', 'name', 'application_type', 'date_created', 'benchmark', 'is_delete', 'total_duration')


class AssessmentFeedbackSerializer(serializers.ModelSerializer):

    class Meta:
        model = AssessmentFeedback
        fields = ('assessment', 'applicant_info', 'feedback', 'reaction')

    def validate(self, attrs):
        q = AssessmentFeedback.objects.filter(assessment=attrs['assessment'],
                                              applicant_info=attrs['applicant_info'],
                                              reaction=attrs['reaction']
                                              )
        if q.exists():
            raise serializers.ValidationError(
                'You already gave a feedback for the assessment')

        return attrs


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ('question_text',)


class OpenEndedSerializer(serializers.ModelSerializer):
    question = QuestionSerializer()

    class Meta:
        model = OpenEndedAnswer
        fields = ('id', "is_correct", "question",
                  "answer_text", "is_marked", "category")


class CategoryNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('category_info', 'name', 'test_duration',
                  'num_of_questions', 'created_date')


class AssessmentSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentSession
        fields = ('date_created', 'device', 'browser', 'location',
                  'enable_webcam', 'full_screen_active')


class CandidateCategoryResultSerializer(serializers.ModelSerializer):
    no_of_questions = serializers.SerializerMethodField()
    percentage_mark = serializers.SerializerMethodField()
    open_ended_questions = serializers.SerializerMethodField()
    session = serializers.SerializerMethodField()
    category = CategoryNameSerializer()

    class Meta:
        model = CategoryResult
        fields = ('category', 'score', 'status', 'no_of_questions',
                  'percentage_mark', 'session',
                  'open_ended_questions')

    def get_no_of_questions(self, objs):
        return Question.objects.filter(test_category_id=objs.category.pk).count()

    def get_percentage_mark(self, objs):

        return (objs.score / self.get_no_of_questions(objs)) * 100

    def get_open_ended_questions(self, objs):
        opa_answer = OpenEndedAnswer.objects.filter(
            candidate=objs.result.candidate, category=objs.category)
        return OpenEndedSerializer(opa_answer, many=True).data

    def get_session(self, objs):
        q = AssessmentSession.objects.get(assessment=objs.result.assessment, category=objs.category,
                                          candidate_id=objs.result.candidate)
        return AssessmentSessionSerializer(q).data


class CandidateResultSerializer(serializers.ModelSerializer):
    category_info = CandidateCategoryResultSerializer(many=True)
    assessment = AssessmentSerializer()
    result_total = serializers.IntegerField()
    assessment_category_count = serializers.IntegerField()

    class Meta:
        model = Result
        fields = (
            'id', 'candidate', 'is_active', 'assessment_category_count', 'assessment', 'result_status',
            'percentage_total', 'duration',
            'result_total', 'applicant_info',
            'category_info')
        extra_kwargs = {'category_info': {'read_only': True}}


class ResultListSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    applicant_id = serializers.SerializerMethodField()
    program = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    applicant_result = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = Result
        fields = ('id', 'name', 'applicant_id', 'program',
                  'email', 'applicant_result', 'status')

    def get_name(self, objs):
        return objs.applicant_info.get('name')

    def get_applicant_id(self, objs):
        return objs.applicant_info.get('applicant_id')

    def get_program(self, objs):
        return objs.applicant_info.get('course')

    def get_email(self, objs):
        return objs.applicant_info.get('email')

    def get_applicant_result(self, objs):
        return round(objs.percentage_total, 2)

    def get_status(self, objs):
        return objs.result_status


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
            opa_answer = OpenEndedAnswer.objects.get(
                pk=validated_data.get('opa_pk'))
            print(opa_answer)
            if opa_answer.is_marked:
                q = CategoryResult.objects.get(result_id=validated_data.get('result_id'),
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
                q = CategoryResult.objects.get(result_id=validated_data.get('result_id'),
                                               category=validated_data.get('category'))
                q.score += 1
                q.save()

            return validated_data

        except OpenEndedAnswer.DoesNotExist:
            raise serializers.ValidationError('Invalid Data Provided')


class ResultInitializerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = ('assessment', 'applicant_info')

    def create(self, validated_data):
        Result.object.create(assessment=validated_data.get('assessment'),
                             applicant_info=validated_data.get(
                                 'applicant_info'),
                             candidate=validated_data.get(
                                 'applicant_info').applicantId
                             )
        return validated_data
