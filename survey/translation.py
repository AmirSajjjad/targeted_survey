from django.utils.translation import gettext_lazy as _


class Translation:
    survey_status_is_publish = _("survey status is publish")
    survey_dont_have_question = _("this survey dont have any question")
    invalid_survey_id = _("invalid survey id")
    unique_question_priorities = _("question priorities in not unique")
    question_minimum_option = _("you have some option type question that dont have minimum 2 option")
    condition_question_priorities = _("check question priorities, have conflict with conditions")
    operation_priorities = _("check operation priorities")
    operation_between_condition = _("check operation between all condition")
    invalid_question_id = _("invalid question id")
    invalid_question_type = _("invalid question type")
    invalid_target_question_priority = _("target question priority must greater than source question priority")
    invalid_option_id = _("invalid option id")
    invalid_numerical_condition_value = _("value of numerical condition must be int")
    condition_only_text_quextion = _("this conditions only allowed for text type question")
    change_first_second_condition = _("change first_condition or second_condition")
    condition_in_one_survey = _("target question in first_condition and second_condition must be equal")
    answer_required_question = _("answer to required question first")
    invalid_answer = _("Invalid answer")
    this_question_required = _("this question is required")
    you_answered_to_survey = _("You are before answered to this survey")
    condition_failed = _("Condition Failed")
    firsy_question = _("this is first question")
    invalid_source_or_target_survey = _("source or target question not in your survey")
    invalid_condition = _("invalid condition")