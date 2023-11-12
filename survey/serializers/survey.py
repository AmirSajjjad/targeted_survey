from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from survey.models import Survey
from survey.translation import Translation


class SurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = Survey
        fields = '__all__'
        read_only_fields  = ['status']

    def validate(self, attrs):
        if self.instance:
            if self.instance.status == Survey.StatusType.publish:
                raise ValidationError(Translation.survey_status_is_publish)
        return super().validate(attrs)

class SurveyPublishSerializer(serializers.Serializer):
    message = serializers.CharField()
