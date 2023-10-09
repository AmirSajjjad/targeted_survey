from django.urls import path
from rest_framework.routers import DefaultRouter

from survey.views.survey import SurveyViewSet, PublishSurveyApiView
from survey.views.question import QuestionViewSet, OptionViewSet, FirstQuestionApiView
from survey.views.conditions import ConditionViewSet, OperatiorViewSet
from survey.views.answer import NextAnswerApiView, PreviousAnswerApiView


router = DefaultRouter()
router.register('', SurveyViewSet, basename="survey")
router.register(r'(?P<survey_id>\d+)/question', QuestionViewSet, basename="question")
router.register(r'question/(?P<question_id>\d+)/option', OptionViewSet, basename="option")
router.register(r'(?P<survey_id>\d+)/condition/operator', OperatiorViewSet, basename="operator")
router.register(r'(?P<survey_id>\d+)/condition', ConditionViewSet, basename="condition")

urlpatterns = [
    path('<int:survey_id>/question/first_question', FirstQuestionApiView.as_view(), name="first_question"),
    path('<int:survey_id>/publish', PublishSurveyApiView.as_view(), name='publish_survey'),
    path('<int:survey_id>/answer/next/<int:question_id>', NextAnswerApiView.as_view(), name='next_answer'),
    path('<int:survey_id>/answer/previous/<int:question_id>', PreviousAnswerApiView.as_view(), name='previous_answer'),
]
urlpatterns += router.urls
