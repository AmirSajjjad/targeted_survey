from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST
from drf_spectacular.utils import extend_schema, OpenApiParameter

from survey.models import Condition, Operatior, Survey
from survey.serializers.conditions import ConditionSerializer, OperatiorSerializer


class ConditionViewSet(viewsets.ModelViewSet):
    serializer_class = ConditionSerializer

    def get_queryset(self):
        return Condition.objects.filter(survey_id=self.kwargs['survey_id'])
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.survey.status == Survey.StatusType.publish:
            return Response(status=HTTP_400_BAD_REQUEST, data="survey status is publish")
        instance.delete()
        return Response(status=HTTP_204_NO_CONTENT)


class OperatiorViewSet(viewsets.ModelViewSet):
    serializer_class = OperatiorSerializer

    def get_queryset(self):
        return Operatior.objects.filter(survey_id=self.kwargs['survey_id'])
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.survey.status == Survey.StatusType.publish:
            return Response(status=HTTP_400_BAD_REQUEST, data="survey status is publish")
        instance.delete()
        return Response(status=HTTP_204_NO_CONTENT)

