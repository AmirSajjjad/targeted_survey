from rest_framework import serializers
from rest_framework.serializers import ValidationError
from survey.models import Condition, Operatior, Survey, Question, Option
from survey.translation import Translation


class ConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Condition
        exclude = ['survey']

    def validate(self, attrs):
        try:
            survey_id = self.context['request'].parser_context["kwargs"]["survey_id"]
            attrs["survey"] = Survey.objects.get(id=survey_id)
        except Survey.DoesNotExist:
            raise serializers.ValidationError(Translation.invalid_survey_id)
        if attrs["survey"].status == Survey.StatusType.publish:
            raise ValidationError(Translation.survey_status_is_publish)
        
        # check source or target question in survey
        if attrs["source_question"].survey != attrs["survey"] or attrs["target_question"].survey != attrs["survey"]:
            raise ValidationError(Translation.invalid_source_or_target_survey)
        
        # source question priority < target question priority
        #    => can not create condition by itself or future question
        if attrs["source_question"].priority >= attrs["target_question"].priority:
            raise ValidationError(Translation.invalid_target_question_priority)
        
        # check source question type with condition field
        if attrs["condition"] in [
            Condition.ConditionType.option_equal,
            Condition.ConditionType.option_not_equal
        ] and attrs["source_question"].question_type == Question.QuestionType.option:
            if not attrs["value"].isdigit():
                raise ValidationError(Translation.invalid_option_id)
            if not Option.objects.filter(id=attrs["value"] , question=attrs["source_question"]).exists():
                raise ValidationError(Translation.invalid_option_id)

        elif attrs["condition"] in [
            Condition.ConditionType.number_lt,
            Condition.ConditionType.number_lte,
            Condition.ConditionType.number_gt,
            Condition.ConditionType.number_gte
        ] and attrs["source_question"].question_type == Question.QuestionType.numerical:
            if not attrs["value"].isdigit():
                raise ValidationError(Translation.invalid_numerical_condition_value)

        elif attrs["condition"] in [
            Condition.ConditionType.text_contain,
            Condition.ConditionType.text_not_contain,
            Condition.ConditionType.text_start,
            Condition.ConditionType.text_not_start,
            Condition.ConditionType.text_end,
            Condition.ConditionType.text_not_end,
        ]:
            if attrs["source_question"].question_type != Question.QuestionType.text:
                raise ValidationError(Translation.condition_only_text_quextion)            
        else:
            raise ValidationError(Translation.invalid_condition)
        
        return super().validate(attrs)


class OperatiorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Operatior
        exclude = ['survey']

    def validate(self, attrs):
        survey_id = self.context['request'].parser_context["kwargs"]["survey_id"]
        attrs["survey"] = Survey.objects.get(id=survey_id)

        if attrs["survey"].status == Survey.StatusType.publish:
            raise ValidationError(Translation.survey_status_is_publish)
        
        if attrs["first_condition"] == attrs["second_condition"]:
            raise ValidationError(Translation.change_first_second_condition)
        
        if attrs["first_condition"].target_question != attrs["second_condition"].target_question:
            raise ValidationError(Translation.condition_in_one_survey)
        
        return super().validate(attrs)
