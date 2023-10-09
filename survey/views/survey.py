from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_204_NO_CONTENT, HTTP_404_NOT_FOUND
from django.db.models import Q, F, Count

from survey.models import Survey, Question, Condition, Operatior
from survey.serializers.survey import SurveySerializer


class SurveyViewSet(viewsets.ModelViewSet):
    serializer_class = SurveySerializer
    queryset = Survey.objects.all()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status == Survey.StatusType.publish:
            return Response(status=HTTP_400_BAD_REQUEST, data="survey status is publish")
        instance.delete()
        return Response(status=HTTP_204_NO_CONTENT)


class PublishSurveyApiView(APIView):
    def get(self, request, *args, **kwargs):
        survey = Survey.objects.filter(id=self.kwargs['survey_id']).exclude(status=Survey.StatusType.publish).first()
        if not survey:
            return Response(status=HTTP_404_NOT_FOUND, data={"detail": "Not found."})
        questions = Question.objects.filter(survey=survey)
        conditions = Condition.objects.filter(survey=survey)
        operations = Operatior.objects.filter(survey=survey)

        # check the survey have question
        if not questions.exists():
            return Response(status=HTTP_400_BAD_REQUEST, data="this survey dont have any question")
        
        # check all question have unique priorities
        if questions.count() != questions.filter(priority__isnull=False).values_list("priority").distinct().count():
            return Response(status=HTTP_400_BAD_REQUEST, data="check question priorities")

        # check all question with type option, have minimum 2 option
        if questions.filter(question_type=Question.QuestionType.option).annotate(num_options=Count('option')).filter(
            num_options__lte=1).exists():
            d = "you have some option type question that dont have minimum 2 option"
            return Response(status=HTTP_400_BAD_REQUEST, data=d)

        # double check source question priority < target question priority (maybe question updated later):
        if conditions.filter(source_question__priority__gte=F('target_question__priority')).exists():
            d = "check question priorities, have conflict with conditions"
            return Response(status=HTTP_400_BAD_REQUEST, data=d)

        # operation validation
        # TODO NEED OPTIMIZATION
        for question_with_condition in conditions.values_list("target_question").distinct():
            qwc = question_with_condition[0]

            question_condition = conditions.filter(target_question=qwc)
            # one condition dont need operation
            if question_condition.count() <= 1:
                continue

            question_operations = operations.filter(
                Q(first_condition__target_question=qwc) | Q(second_condition__target_question=qwc))

            # check operations have unique priorities
            if question_operations.count() != question_operations.values_list("priority").distinct().count():
                return Response(status=HTTP_400_BAD_REQUEST, data="check operation priorities")

            # check operation between all condition in any question
            used_condition_ids = question_operations.values_list('first_condition_id', 'second_condition_id')
            unique_used_condition_ids = set()
            for i, j in used_condition_ids:
                unique_used_condition_ids.add(i)
                unique_used_condition_ids.add(j)
            if question_condition.exclude(id__in=unique_used_condition_ids).exists():
                return Response(status=HTTP_400_BAD_REQUEST, data="check operation between all condition")

        survey.status = Survey.StatusType.publish
        survey.save()
        return Response({"message": "done"})

