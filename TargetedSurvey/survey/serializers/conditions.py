from rest_framework import serializers
from rest_framework.serializers import ValidationError
from survey.models import Condition, Operatior, Survey, Question, Option


class ConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Condition
        exclude = ['survey']

    def validate(self, attrs):
        survey_id = self.context['request'].parser_context["kwargs"]["survey_id"]
        attrs["survey"] = Survey.objects.get(id=survey_id)
        if attrs["survey"].status == Survey.StatusType.publish:
            raise ValidationError("survey status is publish")
        
        # source question priority < target question priority
        #    => can not create condition by itself or future question
        if attrs["source_question"].priority >= attrs["target_question"].priority:
            raise ValidationError("target question priority must greater than source question priority")
        
        # check source question type with condition field
        if attrs["condition"] in [
            Condition.ConditionType.option_equal,
            Condition.ConditionType.option_not_equal
        ] and attrs["source_question"].question_type == Question.QuestionType.option:
            if not attrs["value"].isdigit():
                raise ValidationError('invalid option id')
            if not Option.objects.filter(id=attrs["value"] , question=attrs["source_question"]).exists():
                raise ValidationError('invalid option id')

        elif attrs["condition"] in [
            Condition.ConditionType.number_lt,
            Condition.ConditionType.number_lte,
            Condition.ConditionType.number_gt,
            Condition.ConditionType.number_gte
        ] and attrs["source_question"].question_type == Question.QuestionType.numerical:
            if not attrs["value"].isdigit():
                raise ValidationError('value of numerical condition must be int')

        elif attrs["condition"] in [
            Condition.ConditionType.text_contain,
            Condition.ConditionType.text_not_contain,
            Condition.ConditionType.text_start,
            Condition.ConditionType.text_not_start,
            Condition.ConditionType.text_end,
            Condition.ConditionType.text_not_end,
        ]:
            if attrs["source_question"].question_type != Question.QuestionType.text:
                raise ValidationError('this conditions only allowed for text type question')            
        else:
            raise ValidationError("invalid condition")
        
        return super().validate(attrs)


class OperatiorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Operatior
        exclude = ['survey']

    def validate(self, attrs):
        survey_id = self.context['request'].parser_context["kwargs"]["survey_id"]
        attrs["survey"] = Survey.objects.get(id=survey_id)

        if attrs["survey"].status == Survey.StatusType.publish:
            raise ValidationError("survey status is publish")
        
        if attrs["first_condition"] == attrs["second_condition"]:
            raise ValidationError("change first_condition or second_condition")
        
        if attrs["first_condition"].target_question != attrs["second_condition"].target_question:
            raise ValidationError("target question in first_condition and second_condition must be equal")
        
        return super().validate(attrs)
