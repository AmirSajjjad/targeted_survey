from django.contrib import admin
from survey.models import (
    Survey,
    Question,
    Option,
    Condition,
    Operatior,
    UserAnsweredToSurvey,
    Answer
)

admin.site.register(Survey)
admin.site.register(Question)
admin.site.register(Option)
admin.site.register(Condition)
admin.site.register(Operatior)
admin.site.register(UserAnsweredToSurvey)
admin.site.register(Answer)
