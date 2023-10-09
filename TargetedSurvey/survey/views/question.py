from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

from survey.models import Question, Option, Survey, Condition
from survey.serializers.question import QuestionSerializer, OptionSerializer


class QuestionViewSet(viewsets.ModelViewSet):
    serializer_class = QuestionSerializer

    def get_queryset(self):
        return Question.objects.filter(survey_id=self.kwargs['survey_id'])

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.survey.status == Survey.StatusType.publish:
            return Response(status=HTTP_400_BAD_REQUEST, data="survey status is publish")
        instance.delete()
        return Response(status=HTTP_204_NO_CONTENT)


class FirstQuestionApiView(APIView):
    def get(self, request, *args, **kwargs):
        queryset = Question.objects.filter(
            survey_id=self.kwargs['survey_id'], survey__status=Survey.StatusType.publish).order_by("priority").first()
        if not queryset:
            return Response(status=HTTP_404_NOT_FOUND, data={"detail": "Not found."})
        serializer = QuestionSerializer(queryset)
        return Response(serializer.data)


class OptionViewSet(viewsets.ModelViewSet):
    serializer_class = OptionSerializer

    def get_queryset(self):
        return Option.objects.filter(question_id=self.kwargs['question_id'])
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.question.survey.status == Survey.StatusType.publish:
            return Response(status=HTTP_400_BAD_REQUEST, data="survey status is publish")
        Condition.objects.filter(source_question_id=kwargs["question_id"], value=kwargs["pk"]).delete()
        instance.delete()
        return Response(status=HTTP_204_NO_CONTENT)
