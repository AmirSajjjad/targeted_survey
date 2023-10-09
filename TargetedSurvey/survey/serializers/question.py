from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from survey.models import Question, Option, Survey, Condition


class QuestionSerializer(serializers.ModelSerializer):
    options = serializers.SerializerMethodField()

    class Meta:
        model = Question
        exclude = ['survey']

    def get_options(self, value):
        if value.question_type == Question.QuestionType.option:
            option = Option.objects.filter(question=value.id)
            op = OptionSerializer(option, many=True)
            return op.data
        return None

    def validate(self, attrs):
        survey_id = self.context['request'].parser_context["kwargs"]["survey_id"]
        attrs["survey"] = Survey.objects.get(id=survey_id)
        if attrs["survey"].status == Survey.StatusType.publish:
            raise ValidationError("survey status is publish")

        if self.instance:
            if "question_type" in attrs.keys():
                if attrs["question_type"] != self.instance.question_type:
                    Condition.objects.filter(survey_id=survey_id, source_question=self.instance).delete()
                    Option.objects.filter(question=self.instance).delete()            
            
        return super().validate(attrs)


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
            model = Option
            exclude = ['question']

    def validate(self, attrs):
        question_id = self.context['request'].parser_context["kwargs"]["question_id"]
        try:
            attrs["question"] = Question.objects.get(id=question_id)
        except Question.DoesNotExist:
            raise serializers.ValidationError("invalid question id")
        
        if attrs["question"].survey.status == Survey.StatusType.publish:
            raise ValidationError("survey status is publish")
            
        if attrs["question"].question_type != Question.QuestionType.option:
            raise serializers.ValidationError("invalid question type")
        
        return super().validate(attrs)
