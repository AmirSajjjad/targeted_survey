from rest_framework import serializers
from rest_framework.exceptions import ValidationError, NotFound

from survey.models import Question, Option, Survey, Condition
from survey.translation import Translation


class QuestionSerializer(serializers.ModelSerializer):
    options = serializers.SerializerMethodField()

    class Meta:
        model = Question
        exclude = ['survey']

    def get_options(self, value) -> list:
        if value.question_type == Question.QuestionType.option:
            option = Option.objects.filter(question=value.id)
            op = OptionSerializer(option, many=True)
            return op.data
        return None

    def validate(self, attrs):
        survey_id = self.context['request'].parser_context["kwargs"]["survey_id"]
        try:
            attrs["survey"] = Survey.objects.get(id=survey_id)
        except Survey.DoesNotExist:
            raise NotFound()
        if attrs["survey"].status == Survey.StatusType.publish:
            raise ValidationError(Translation.survey_status_is_publish)

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
            raise serializers.ValidationError(Translation.invalid_question_id)
        
        if attrs["question"].survey.status == Survey.StatusType.publish:
            raise ValidationError(Translation.survey_status_is_publish)
            
        if attrs["question"].question_type != Question.QuestionType.option:
            raise serializers.ValidationError(Translation.invalid_question_type)
        
        return super().validate(attrs)
