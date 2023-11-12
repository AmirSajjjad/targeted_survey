from rest_framework.test import APITestCase

from survey.models import Survey, Question, Option, Condition, Operatior
from survey.translation import Translation

class TestSurveyCRUD(APITestCase):
    def setUp(self):
        self.draft_survey = Survey.objects.create(title="default publish survey")
        self.publish_survey = Survey.objects.create(title="default publish survey", status=Survey.StatusType.publish)
    
    def test_create_survey(self):
        survey_data = {
            "title": "test create survey"
        }
        response = self.client.post('/api/survey/', data=survey_data)
        self.assertEqual(response.status_code, 201)
        survey_object = Survey.objects.get(title=survey_data["title"])
        response_data = response.json()
        self.assertEqual(response_data["id"], survey_object.id)
        self.assertEqual(response_data["title"], survey_object.title)
        self.assertEqual(response_data["status"], survey_object.status)

    def test_list_survey(self):
        response = self.client.get('/api/survey/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)

    def test_retrive_survey(self):
        response = self.client.get('/api/survey/xxx/')
        self.assertEqual(response.status_code, 404)
        response = self.client.get('/api/survey/999/')
        self.assertEqual(response.status_code, 404)
        response = self.client.get(f'/api/survey/{self.draft_survey.id}/')
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data["id"], self.draft_survey.id)
        self.assertEqual(response_data["title"], self.draft_survey.title)
        self.assertEqual(response_data["status"], self.draft_survey.status)

    def test_update_survey(self):
        # put:
        response = self.client.put('/api/survey/xxx/')
        self.assertEqual(response.status_code, 404)
        response = self.client.put('/api/survey/999/')
        self.assertEqual(response.status_code, 404)
        # patch:
        response = self.client.patch('/api/survey/xxx/')
        self.assertEqual(response.status_code, 404)
        response = self.client.patch('/api/survey/999/')
        self.assertEqual(response.status_code, 404)

        survey_data = {
            "title": "updated survey title",
            "status": "publish"
        }
        # put:
        response = self.client.put(f'/api/survey/{self.draft_survey.id}/', data=survey_data)
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data["id"], self.draft_survey.id)
        self.assertEqual(response_data["title"], survey_data["title"])
        self.assertEqual(response_data["status"], self.draft_survey.status)
        response = self.client.put(f'/api/survey/{self.publish_survey.id}/', data=survey_data)
        self.assertEqual(response.status_code, 400)
        # patch:
        response = self.client.patch(f'/api/survey/{self.draft_survey.id}/', data=survey_data)
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data["id"], self.draft_survey.id)
        self.assertEqual(response_data["title"], survey_data["title"])
        self.assertEqual(response_data["status"], self.draft_survey.status)
        response = self.client.patch(f'/api/survey/{self.publish_survey.id}/', data=survey_data)
        self.assertEqual(response.status_code, 400)

    def test_delete_survey(self):
        response = self.client.delete('/api/survey/xxx/')
        self.assertEqual(response.status_code, 404)
        response = self.client.delete('/api/survey/999/')
        self.assertEqual(response.status_code, 404)
        response = self.client.delete(f'/api/survey/{self.draft_survey.id}/')
        self.assertEqual(response.status_code, 204)
        response = self.client.delete(f'/api/survey/{self.publish_survey.id}/')
        self.assertEqual(response.status_code, 400)


class TestPublishSurvey(APITestCase):

    def test_publish_survey(self):
        # test survey id
        response = self.client.get('/api/survey/xxx/publish')
        self.assertEqual(response.status_code, 404)
        response = self.client.get('/api/survey/999/publish')
        self.assertEqual(response.status_code, 404)

        # test publish a published survey
        survey_publish = Survey.objects.create(title="default publish survey", status=Survey.StatusType.publish)
        response = self.client.get(f'/api/survey/{survey_publish.id}/publish')
        self.assertEqual(response.status_code, 404)

        # test survey have question
        survey_empty = Survey.objects.create(title="empty survey")
        response = self.client.get(f'/api/survey/{survey_empty.id}/publish')
        self.assertEqual(response.json(), Translation.survey_dont_have_question)
        self.assertEqual(response.status_code, 400)

        # test unique questions priority
        survey_priority = Survey.objects.create(title="priority survey")
        Question.objects.create(
            title="q1",
            survey=survey_priority,
            question_type=Question.QuestionType.text,
            priority=1
        )
        Question.objects.create(
            title="q2",
            survey=survey_priority,
            question_type=Question.QuestionType.text,
            priority=1
        )
        response = self.client.get(f'/api/survey/{survey_priority.id}/publish')
        self.assertEqual(response.json(), Translation.unique_question_priorities)
        self.assertEqual(response.status_code, 400)

        # test option question
        survey_option = Survey.objects.create(title="option survey")
        qo1 = Question.objects.create(
            title="q1",
            survey=survey_option,
            question_type=Question.QuestionType.option,
            priority=1
        )
        Option.objects.create(title="oo1", question=qo1, priority=1)
        response = self.client.get(f'/api/survey/{survey_option.id}/publish')
        self.assertEqual(response.json(), Translation.question_minimum_option)
        self.assertEqual(response.status_code, 400)

        # test condition: source question priority < target question priority
        survey_condition = Survey.objects.create(title="condition survey")
        qc1 = Question.objects.create(
            title="q1",
            survey=survey_condition,
            question_type=Question.QuestionType.text,
            priority=1
        )
        qc2 = Question.objects.create(
            title="q2",
            survey=survey_condition,
            question_type=Question.QuestionType.text,
            priority=2
        )
        Condition.objects.create(
            survey=survey_condition,
            source_question=qc2,
            target_question=qc1,
            condition=Condition.ConditionType.text_contain,
            value="asd"
        )
        response = self.client.get(f'/api/survey/{survey_condition.id}/publish')
        self.assertEqual(response.json(), Translation.condition_question_priorities)
        self.assertEqual(response.status_code, 400)

        # test operation priority
        survey_operation_priority = Survey.objects.create(title="operation priority")
        qc1 = Question.objects.create(
            title="q1",
            survey=survey_operation_priority,
            question_type=Question.QuestionType.text,
            priority=1
        )
        qc2 = Question.objects.create(
            title="q2",
            survey=survey_operation_priority,
            question_type=Question.QuestionType.text,
            priority=2
        )
        cpp1 = Condition.objects.create(
            survey=survey_operation_priority,
            source_question=qc1,
            target_question=qc2,
            condition=Condition.ConditionType.text_contain,
            value="asd"
        )
        cpp2 = Condition.objects.create(
            survey=survey_operation_priority,
            source_question=qc1,
            target_question=qc2,
            condition=Condition.ConditionType.text_contain,
            value="asd"
        )
        Operatior.objects.create(
            first_condition=cpp1,
            second_condition=cpp2,
            operator=Operatior.OperatorType.and_operator,
            priority=1,
            survey=survey_operation_priority
        )
        Operatior.objects.create(
            first_condition=cpp1,
            second_condition=cpp2,
            operator=Operatior.OperatorType.and_operator,
            priority=1,
            survey=survey_operation_priority
        )
        response = self.client.get(f'/api/survey/{survey_operation_priority.id}/publish')
        self.assertEqual(response.json(), Translation.operation_priorities)
        self.assertEqual(response.status_code, 400)

        # test operation between all condition
        survey_condition_operation = Survey.objects.create(title="condition operation")
        qc1 = Question.objects.create(
            title="q1",
            survey=survey_condition_operation,
            question_type=Question.QuestionType.text,
            priority=1
        )
        qc2 = Question.objects.create(
            title="q2",
            survey=survey_condition_operation,
            question_type=Question.QuestionType.text,
            priority=2
        )
        Condition.objects.create(
            survey=survey_condition_operation,
            source_question=qc1,
            target_question=qc2,
            condition=Condition.ConditionType.text_contain,
            value="asd"
        )
        Condition.objects.create(
            survey=survey_condition_operation,
            source_question=qc1,
            target_question=qc2,
            condition=Condition.ConditionType.text_contain,
            value="asd"
        )
        response = self.client.get(f'/api/survey/{survey_condition_operation.id}/publish')
        self.assertEqual(response.json(), Translation.operation_between_condition)
        self.assertEqual(response.status_code, 400)

        # test OK
        survey_ok = Survey.objects.create(title="ok")
        qc1 = Question.objects.create(
            title="q1",
            survey=survey_ok,
            question_type=Question.QuestionType.text,
            priority=1
        )
        qc2 = Question.objects.create(
            title="q2",
            survey=survey_ok,
            question_type=Question.QuestionType.text,
            priority=2
        )
        cpp1 = Condition.objects.create(
            survey=survey_ok,
            source_question=qc1,
            target_question=qc2,
            condition=Condition.ConditionType.text_contain,
            value="asd"
        )
        cpp2 = Condition.objects.create(
            survey=survey_ok,
            source_question=qc1,
            target_question=qc2,
            condition=Condition.ConditionType.text_contain,
            value="asd"
        )
        Operatior.objects.create(
            first_condition=cpp1,
            second_condition=cpp2,
            operator=Operatior.OperatorType.and_operator,
            priority=1,
            survey=survey_ok
        )
        Operatior.objects.create(
            first_condition=cpp1,
            second_condition=cpp2,
            operator=Operatior.OperatorType.and_operator,
            priority=2,
            survey=survey_ok
        )
        response = self.client.get(f'/api/survey/{survey_ok.id}/publish')
        self.assertEqual(response.status_code, 200)
    