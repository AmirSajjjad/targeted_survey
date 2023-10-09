from rest_framework import serializers

from survey.models import Answer
from survey.serializers.question import QuestionSerializer


class NextAnswerRequestSerializer(serializers.Serializer):
    answer = serializers.CharField(required=False)


class NextPreviousAnswerResponseSerializer(serializers.Serializer):
    question = QuestionSerializer()
    answer = serializers.CharField()
    finished = serializers.BooleanField(required=False)
