from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import HttpResponseBadRequest
from django.db.models import Q

from survey.models import Survey, Question, Answer, Condition, Option, UserAnsweredToSurvey, Operatior
from survey.serializers.answer import NextAnswerRequestSerializer, NextPreviousAnswerResponseSerializer


class AnswerBussinesLogic:
            
    @staticmethod
    def check_last_required_questions(answers, questions, target_question, survey_conditions):
        answer_ids = answers.values_list('question')
        answer_ids = [i[0] for i in answer_ids]
        # find required question without answer that priority less than target question priority
        required_question_without_answer = questions.filter(
            priority__lt=target_question.priority, required=True).exclude(id__in=answer_ids)
        for rqwa in required_question_without_answer:
            conditions = survey_conditions.filter(target_question=rqwa)
            if conditions.exists():
                if AnswerBussinesLogic.check_condition(conditions, answers):
                    return True, "answer to required question first"
            else:
                return True, "answer to required question first"
        return False, None
    
    @staticmethod
    def check_condition(condition_objects, answers):
        conditions_result = {}
        for co in condition_objects:
            question = co.source_question
            try:
                user_answer = answers.get(question=question)
            except Answer.DoesNotExist():
                return False
            condition = co.condition
            value = co.value

            if condition == Condition.ConditionType.option_equal:
                conditions_result[co] = value == str(user_answer.option_id)
            elif condition == Condition.ConditionType.option_not_equal:
                conditions_result[co] = value != str(user_answer.option_id)
            elif condition == Condition.ConditionType.number_lt:
                conditions_result[co] = int(value) > int(user_answer.text)
            elif condition == Condition.ConditionType.number_lte:
                conditions_result[co] = int(value) >= int(user_answer.text)
            elif condition == Condition.ConditionType.number_gt:
                conditions_result[co] = int(value) < int(user_answer.text)
            elif condition == Condition.ConditionType.number_gte:
                conditions_result[co] = int(value) <= int(user_answer.text)
            elif condition == Condition.ConditionType.text_contain:
                conditions_result[co] = value in user_answer.text
            elif condition == Condition.ConditionType.text_not_contain:
                conditions_result[co] = value not in user_answer.text
            elif condition == Condition.ConditionType.text_start:
                conditions_result[co] = user_answer.text.startswith(value)
            elif condition == Condition.ConditionType.text_not_start:
                conditions_result[co] = not user_answer.text.startswith(value)
            elif condition == Condition.ConditionType.text_end:
                conditions_result[co] = user_answer.text.endswith(value)
            elif condition == Condition.ConditionType.text_not_end:
                conditions_result[co] = not user_answer.text.endswith(value)

        if len(conditions_result.keys()) == 0:
            return True
        if len(conditions_result.keys()) == 1:
            return conditions_result[co]
        
        operators = Operatior.objects.filter(
            Q(first_condition__in=condition_objects) | Q(second_condition__in=condition_objects)).order_by("priority")
        for operator in operators:
            if operator.operator == Operatior.OperatorType.and_operator:
                return conditions_result[operator.first_condition] and conditions_result[operator.second_condition]
            elif operator.operator == Operatior.OperatorType.or_operator:
                return conditions_result[operator.first_condition] or conditions_result[operator.second_condition]
            elif operator.operator == Operatior.OperatorType.xor_operator:
                return conditions_result[operator.first_condition] ^ conditions_result[operator.second_condition]

    @staticmethod
    def check_user_answered_before(user_answer, old_answer, target_question, answers):
        if user_answer and old_answer:
            after_answer = answers.filter(question__priority__gt=target_question.priority).order_by(
                "question__priority").values_list("question_id") #  check order ***************************************************************
            if after_answer.exists():  # survey have answer with greater priority
                old_answer_value = old_answer.text if old_answer.text else old_answer.option
                if str(old_answer_value) != user_answer["answer"]:  # check answer edited
                    after_answer = [i[0] for i in after_answer]
                    conditions = Condition.objects.filter(source_question=after_answer)
                    # check condition have a question condition with source question that have answer
                    if conditions.exists():
                        answers.filter(question__priority__gte=conditions.first().question.priority).delete()

    @staticmethod
    def save_answer(user_answer, old_answer, target_question, user):
        if user_answer:
            # validate answer with question type
            if target_question.question_type == Question.QuestionType.numerical:
                try:
                    float(user_answer)
                except ValueError:
                    return True, "Invalid answer"
            elif target_question.question_type == Question.QuestionType.option:
                try:
                    user_answer = Option.objects.get(id=user_answer, question=target_question)
                except Option.DoesNotExist:
                    return True, "Invalid answer"
                except ValueError:
                    return True, "Invalid answer"
                
            # check create or update answer
            if old_answer:
                if target_question.question_type in [Question.QuestionType.numerical, Question.QuestionType.text]:
                    old_answer.text = user_answer
                else:
                    old_answer.option = user_answer
                old_answer.save()
            else:
                if target_question.question_type in [Question.QuestionType.numerical, Question.QuestionType.text]:
                    Answer.objects.create(user=user, question=target_question, text=user_answer)
                else:
                    Answer.objects.create(user=user, question=target_question, option=user_answer)
        else:
            # check user can not skip required question without answer
            if not old_answer and target_question.required:
                return True, "this question is required"
        
        return False, None
    

class NextAnswerApiView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = NextAnswerRequestSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_answer = serializer.data
        user_answer = user_answer.get("answer", None)
        survey = get_object_or_404(Survey, id=self.kwargs['survey_id'], status=Survey.StatusType.publish)
        questions = Question.objects.filter(survey=survey)
        target_question = get_object_or_404(questions, id=self.kwargs['question_id'], survey=survey)
        next_questions = questions.filter(priority__gt=target_question.priority).order_by("priority")
        survey_condition = Condition.objects.filter(survey=survey)
        current_question_conditions = survey_condition.filter(target_question=target_question)
        answers = Answer.objects.filter(question__survey=survey, user=request.user)
        old_answer = answers.filter(question=target_question).last()

        # check user can not change answer if before finished this survey
        if UserAnsweredToSurvey.objects.filter(survey=survey, user=request.user).exists():
            return HttpResponseBadRequest("You are before answered to this survey")
        
        # check last required questions
        error, message = AnswerBussinesLogic.check_last_required_questions(answers, questions, target_question,
                                                                           survey_condition)
        if error:
            return error, message
        
        # Check current Condition
        if current_question_conditions.exists():
            if not AnswerBussinesLogic.check_condition(current_question_conditions, answers):
                return HttpResponseBadRequest("Condition Failed")
        
        # if user answered to this question before and now send a answer
        AnswerBussinesLogic.check_user_answered_before(user_answer, old_answer, target_question, answers)

        # check and save answer
        error, message = AnswerBussinesLogic.save_answer(user_answer, old_answer, target_question, request.user)
        if error:
            return HttpResponseBadRequest(message)
        
        d = {"question": None, "answer": None, "finished": True}
        for next_question in next_questions:
            # Check next question conditions
            next_question_conditions = survey_condition.filter(target_question=next_question)
            if AnswerBussinesLogic.check_condition(next_question_conditions, answers):
                next_answer = answers.filter(question=next_question).last()
                if next_answer:
                    next_answer = next_answer.text if next_answer.text else next_answer.option_id
                d["question"] = next_question
                d["answer"] = next_answer
                d["finished"] = False
                break
        
        if d["finished"]:
            UserAnsweredToSurvey.objects.create(user=request.user, survey=survey)
        serializer = NextPreviousAnswerResponseSerializer(d)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class PreviousAnswerApiView(APIView):
    def get(self, request, *args, **kwargs):
        survey = get_object_or_404(Survey, id=self.kwargs['survey_id'], status=Survey.StatusType.publish)
        survey_condition = Condition.objects.filter(survey=survey)
        questions = Question.objects.filter(survey=survey)
        target_question = get_object_or_404(questions, id=self.kwargs['question_id'])
        previous_questions = questions.filter(
            survey=survey, priority__lt=target_question.priority).order_by("-priority")
        answers = Answer.objects.filter(question__survey=survey, user=request.user)
        
        for previous_question in previous_questions:
            previous_question_conditions = survey_condition.filter(target_question=previous_question)
            if AnswerBussinesLogic.check_condition(previous_question_conditions, answers):
                previous_answer = Answer.objects.filter(user=request.user, question=previous_question).last()
                if previous_answer:
                    previous_answer = previous_answer.text if previous_answer.text else previous_answer.option_id
                d = {"question": previous_question, "answer": previous_answer}
                serializer = NextPreviousAnswerResponseSerializer(d)
                return Response(data=serializer.data, status=status.HTTP_200_OK)
        return HttpResponseBadRequest("this is first question")
