from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class Survey(models.Model):
    class StatusType(models.TextChoices):
        draft = "draft", _("draft")
        publish = "publish", _("publish")

    title = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=StatusType.choices, default=StatusType.draft)


class Question(models.Model):
    class QuestionType(models.TextChoices):
        option = "option", _("option")
        text = "text", _("text")
        numerical = "numerical", _("numerical")
        
    title = models.CharField(max_length=200)
    survey = models.ForeignKey("Survey", on_delete=models.CASCADE)
    question_type = models.CharField(max_length=10, choices=QuestionType.choices)
    required = models.BooleanField(default=False)
    priority = models.IntegerField()


class Option(models.Model):
    title = models.CharField(max_length=200)
    question = models.ForeignKey("Question", on_delete=models.CASCADE)
    priority = models.IntegerField(null=True, blank=True)


class Condition(models.Model):
    # with this model we decision to show the question or skip

    class ConditionType(models.TextChoices):
        # option conditions:
        option_equal = "option_equal", _("option_equal")
        option_not_equal = "option_not_equal", _("option_not_equal")
        # numerical conditions:
        number_lt = "number_lt", _("number_lt")
        number_lte = "number_lte", _("number_lte")
        number_gt = "number_gt", _("number_gt")
        number_gte = "number_gte", _("number_gte")
        # text conditions:
        text_contain = "text_contain", _("text_contain")
        text_not_contain = "text_not_contain", _("text_not_contain")
        text_start = "text_start", _("text_start")
        text_not_start = "text_not_start", _("text_not_start")
        text_end = "text_end", _("text_end")
        text_not_end = "text_not_end", _("text_not_end")
        # for required question
        # have answer
        # dont have answer


    survey = models.ForeignKey("Survey", on_delete=models.CASCADE)
    # source_question is a question that have conditions
    source_question = models.ForeignKey("Question", on_delete=models.CASCADE, related_name="source_question")
    # target_question is a question that decision to show or skip
    target_question = models.ForeignKey("Question", on_delete=models.CASCADE, related_name="target_question")
    condition = models.CharField(max_length=20, choices=ConditionType.choices)
    value = models.CharField(max_length=200)


class Operatior(models.Model):  # operatior between conditions
    class OperatorType(models.TextChoices):
        and_operator = "and_operator", _("and_operator")
        or_operator = "or_operator", _("or_operator")
        xor_operator = "xor_operator", _("xor_operator")

    first_condition = models.ForeignKey("Condition", on_delete=models.CASCADE, related_name="first_condition")
    second_condition = models.ForeignKey("Condition", on_delete=models.CASCADE, related_name="second_condition")
    operator = models.CharField(max_length=20, choices=OperatorType.choices)
    priority = models.IntegerField()
    survey = models.ForeignKey("Survey", on_delete=models.CASCADE)


class UserAnsweredToSurvey(models.Model):
    # with this model we understand users answered to a survey complitly
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    survey = models.ForeignKey("Survey", on_delete=models.CASCADE)


class Answer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey("Question", on_delete=models.CASCADE)
    text = models.TextField(null=True, blank=True)
    option = models.ForeignKey("Option", null=True, blank=True, on_delete=models.CASCADE)
