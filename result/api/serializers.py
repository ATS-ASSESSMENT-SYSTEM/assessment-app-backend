import json
from rest_framework import serializers
from django.db.models import Exists

from result.models import Result, Category_Result
from assessment.models import Assessment
from questions_category.models import Category


class AssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assessment
        fields = ('name',)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'result')


class CategoryScoreSerializer(serializers.ModelSerializer):
    name = serializers.CharField()

    class Meta:
        model = Category_Result
        fields = ('name', 'score')


class ResultSerializer(serializers.ModelSerializer):
    assessment = serializers.CharField(required=True)
    category_score_list = CategoryScoreSerializer(many=True, required=True, write_only=True)

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
            raise serializers.ValidationError('one or more category names are invalid')

        assessment_q = category_instance.filter(assessment__pk=check_assessment.first().pk)

        if not len(category) is assessment_q.count():
            raise serializers.ValidationError('one or more category does not exists in the assessment')

        result_instance = Result.objects.filter(assessment=check_assessment.first(), candidate=candidate)

        if result_instance.exists():
            check_category = Category_Result.objects.filter(category__name__in=category,
                                                            result=result_instance.first()).exists()
            if check_category:
                raise serializers.ValidationError('one or more result category already exists for this candidate')

        return attrs

    def create(self, validated_data):
        ## ask:  why am i getting ordered dict

        assessment = Assessment.objects.get(
            name=validated_data.get('assessment'))
        candidate = validated_data.get('candidate')

        scores = json.loads(json.dumps(validated_data.pop('category_score_list')))

        create_result, created = Result.objects.get_or_create(assessment=assessment,
                                                              candidate=candidate)
        if create_result:
            for dict_element in scores:
                category_instance = Category.objects.get(name=dict_element['name'])
                Category_Result.objects.create(
                    result=create_result, score=dict_element['score'],
                    category=category_instance)
        return create_result
