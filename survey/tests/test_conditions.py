from rest_framework.test import APITestCase

from survey.models import Survey, Question, Condition, Operatior


class TestConditionCRUD(APITestCase):
    def setUp(self):
        self.draft_survey = Survey.objects.create(title="s1")
        self.draft_question1 = Question.objects.create(
            title="q1",
            survey=self.draft_survey,
            question_type=Question.QuestionType.text,
            priority=1
        )
        self.draft_question2 = Question.objects.create(
            title="q2",
            survey=self.draft_survey,
            question_type=Question.QuestionType.text,
            priority=2
        )
        self.draft_condition = Condition.objects.create(
            survey=self.draft_survey,
            source_question=self.draft_question1,
            target_question=self.draft_question2,
            condition=Condition.ConditionType.text_contain,
            value="asd"
        )
        self.publish_survey = Survey.objects.create(title="s2", status=Survey.StatusType.publish)
        self.publish_question1 = Question.objects.create(
            title="q1",
            survey=self.publish_survey,
            question_type=Question.QuestionType.text,
            priority=1
        )
        self.publish_question2 = Question.objects.create(
            title="q2",
            survey=self.publish_survey,
            question_type=Question.QuestionType.text,
            priority=2
        )
        self.publish_condition = Condition.objects.create(
            survey=self.publish_survey,
            source_question=self.publish_question1,
            target_question=self.publish_question1,
            condition=Condition.ConditionType.text_contain,
            value="asd"
        )
    
    def test_list_condition(self):
        # test invalid survey id
        response = self.client.get(f'/api/survey/xxx/condition/')
        self.assertEqual(response.status_code, 404)
        response = self.client.get(f'/api/survey/999/condition/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])
        
        # test list draft/publish survey
        response = self.client.get(f'/api/survey/{self.draft_survey.id}/condition/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        response = self.client.get(f'/api/survey/{self.publish_survey.id}/condition/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
    
    def test_retrive_condition(self):
        # test invalid survey_id and condition_id
        response = self.client.get(f'/api/survey/xxx/condition/xxx/')
        self.assertEqual(response.status_code, 404)
        response = self.client.get(f'/api/survey/999/condition/999/')
        self.assertEqual(response.status_code, 404)

        # test list draft/publish survey
        response = self.client.get(f'/api/survey/{self.draft_survey.id}/condition/{self.draft_condition.id}/')
        response_data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data["id"], self.draft_condition.id)
        self.assertEqual(response_data["source_question"], self.draft_condition.source_question.id)
        self.assertEqual(response_data["target_question"], self.draft_condition.target_question.id)
        self.assertEqual(response_data["condition"], self.draft_condition.condition)
        self.assertEqual(response_data["value"], self.draft_condition.value)
        response = self.client.get(f'/api/survey/{self.publish_survey.id}/condition/{self.publish_condition.id}/')
        response_data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data["id"], self.publish_condition.id)
        self.assertEqual(response_data["source_question"], self.publish_condition.source_question.id)
        self.assertEqual(response_data["target_question"], self.publish_condition.target_question.id)
        self.assertEqual(response_data["condition"], self.publish_condition.condition)
        self.assertEqual(response_data["value"], self.publish_condition.value)

    def test_create_condition(self):
        # test invalid survey id
        draft_data = {
            "source_question": self.draft_question1.id,
            "target_question": self.draft_question2.id,
            "condition": Condition.ConditionType.text_contain,
            "value": "asd"
        }
        response = self.client.post('/api/survey/xxx/condition/', data=draft_data)
        self.assertEqual(response.status_code, 404)
        response = self.client.post('/api/survey/999/condition/', data=draft_data)
        self.assertEqual(response.status_code, 400)

        # test create condition for publish survey
        publish_data = {
            "source_question": self.publish_question1.id,
            "target_question": self.publish_question2.id,
            "condition": Condition.ConditionType.text_contain,
            "value": "asd"
        }
        response = self.client.post(f'/api/survey/{self.publish_survey.id}/condition/', data=publish_data)
        self.assertEqual(response.status_code, 400)

        # test target and source question not in a survey
        data = {
            "source_question": self.publish_question1.id,
            "target_question": self.publish_question2.id,
            "condition": Condition.ConditionType.text_contain,
            "value": "asd"
        }
        response = self.client.post(f'/api/survey/{self.draft_survey.id}/condition/', data=data)
        self.assertEqual(response.status_code, 400)

        # test priority of target and source question
        data = {
            "source_question": self.draft_question2.id,
            "target_question": self.draft_question1.id,
            "condition": Condition.ConditionType.text_contain,
            "value": "asd"
        }
        response = self.client.post(f'/api/survey/{self.draft_survey.id}/condition/', data=data)
        self.assertEqual(response.status_code, 400)

        # test can not create condition with itself
        data = {
            "source_question": self.draft_question1.id,
            "target_question": self.draft_question1.id,
            "condition": Condition.ConditionType.text_contain,
            "value": "asd"
        }
        response = self.client.post(f'/api/survey/{self.draft_survey.id}/condition/', data=data)
        self.assertEqual(response.status_code, 400)

        # test type of source question and condition
        data = {
            "source_question": self.draft_question1.id,
            "target_question": self.draft_question2.id,
            "condition": Condition.ConditionType.number_gt,
            "value": "10"
        }
        response = self.client.post(f'/api/survey/{self.draft_survey.id}/condition/', data=data)
        self.assertEqual(response.status_code, 400)

        # invali source or target question id
        data = {
            "source_question": 999,
            "target_question": self.draft_question2.id,
            "condition": Condition.ConditionType.text_contain,
            "value": "10"
        }
        response = self.client.post(f'/api/survey/{self.draft_survey.id}/condition/', data=data)
        self.assertEqual(response.status_code, 400)
        data = {
            "source_question": self.draft_question1.id,
            "target_question": 999,
            "condition": Condition.ConditionType.text_contain,
            "value": "10"
        }
        response = self.client.post(f'/api/survey/{self.draft_survey.id}/condition/', data=data)
        self.assertEqual(response.status_code, 400)

        # invali value for any type of conditions
        # text type: blank
        data = {
            "source_question": self.draft_question1.id,
            "target_question": self.draft_question2.id,
            "condition": Condition.ConditionType.text_contain,
            "value": ""
        }
        response = self.client.post(f'/api/survey/{self.draft_survey.id}/condition/', data=data)
        self.assertEqual(response.status_code, 400)

        # number type: text
        number_question = Question.objects.create(
            title="q1",
            survey=self.draft_survey,
            question_type=Question.QuestionType.numerical,
            priority=1
        )
        data = {
            "source_question": number_question.id,
            "target_question": self.draft_question2.id,
            "condition": Condition.ConditionType.number_gt,
            "value": "asd"
        }
        response = self.client.post(f'/api/survey/{self.draft_survey.id}/condition/', data=data)
        self.assertEqual(response.status_code, 400)
        
        # option type: text - invalid id
        option_question = Question.objects.create(
            title="q1",
            survey=self.draft_survey,
            question_type=Question.QuestionType.option,
            priority=1
        )
        data = {
            "source_question": option_question.id,
            "target_question": self.draft_question2.id,
            "condition": Condition.ConditionType.option_equal,
            "value": "asd"
        }
        response = self.client.post(f'/api/survey/{self.draft_survey.id}/condition/', data=data)
        self.assertEqual(response.status_code, 400)

        # test OK
        response = self.client.post(f'/api/survey/{self.draft_survey.id}/condition/', data=draft_data)
        self.assertEqual(response.status_code, 201)
    
    def test_update_condition(self):
        # test invalid survey id
        draft_data = {
            "source_question": self.draft_question1.id,
            "target_question": self.draft_question2.id,
            "condition": Condition.ConditionType.text_contain,
            "value": "asd"
        }
        response = self.client.put('/api/survey/xxx/condition/xxx/', data=draft_data)
        self.assertEqual(response.status_code, 404)
        response = self.client.patch('/api/survey/xxx/condition/xxx/', data=draft_data)
        self.assertEqual(response.status_code, 404)
        response = self.client.put('/api/survey/999/condition/999/', data=draft_data)
        self.assertEqual(response.status_code, 404)
        response = self.client.patch('/api/survey/999/condition/999/', data=draft_data)
        self.assertEqual(response.status_code, 404)

        # test invalid condition id
        response = self.client.put(f'/api/survey/{self.draft_survey.id}/condition/xxx/', data=draft_data)
        self.assertEqual(response.status_code, 404)
        response = self.client.patch(f'/api/survey/{self.draft_survey.id}/condition/xxx/', data=draft_data)
        self.assertEqual(response.status_code, 404)
        response = self.client.put(f'/api/survey/{self.draft_survey.id}/condition/999/', data=draft_data)
        self.assertEqual(response.status_code, 404)
        response = self.client.patch(f'/api/survey/{self.draft_survey.id}/condition/999/', data=draft_data)
        self.assertEqual(response.status_code, 404)

        # test update condition for publish survey
        data = {
            "source_question": self.publish_question1.id,
            "target_question": self.publish_question2.id,
            "condition": Condition.ConditionType.text_contain,
            "value": "asd"
        }
        response = self.client.put(f'/api/survey/{self.publish_survey.id}/condition/{self.publish_condition.id}/',
                                     data=data)
        self.assertEqual(response.status_code, 400)
        response = self.client.patch(f'/api/survey/{self.publish_survey.id}/condition/{self.publish_condition.id}/',
                                     data=data)
        self.assertEqual(response.status_code, 400)

        # test target and source question not in a survey
        data = {
            "source_question": self.publish_question1.id,
            "target_question": self.publish_question2.id,
            "condition": Condition.ConditionType.text_contain,
            "value": "asd"
        }
        response = self.client.put(f'/api/survey/{self.draft_survey.id}/condition/{self.draft_condition.id}/', data=data)
        self.assertEqual(response.status_code, 400)
        response = self.client.patch(f'/api/survey/{self.draft_survey.id}/condition/{self.draft_condition.id}/', data=data)
        self.assertEqual(response.status_code, 400)

        # test priority of target and source question
        data = {
            "source_question": self.draft_question2.id,
            "target_question": self.draft_question1.id,
            "condition": Condition.ConditionType.text_contain,
            "value": "asd"
        }
        response = self.client.put(f'/api/survey/{self.draft_survey.id}/condition/{self.draft_condition.id}/', data=data)
        self.assertEqual(response.status_code, 400)
        response = self.client.patch(f'/api/survey/{self.draft_survey.id}/condition/{self.draft_condition.id}/', data=data)
        self.assertEqual(response.status_code, 400)

        # test can not create condition with itself
        data = {
            "source_question": self.draft_question1.id,
            "target_question": self.draft_question1.id,
            "condition": Condition.ConditionType.text_contain,
            "value": "asd"
        }
        response = self.client.put(f'/api/survey/{self.draft_survey.id}/condition/{self.draft_condition.id}/', data=data)
        self.assertEqual(response.status_code, 400)
        response = self.client.patch(f'/api/survey/{self.draft_survey.id}/condition/{self.draft_condition.id}/', data=data)
        self.assertEqual(response.status_code, 400)

        # test type of source question and condition
        data = {
            "source_question": self.draft_question1.id,
            "target_question": self.draft_question2.id,
            "condition": Condition.ConditionType.number_gt,
            "value": "10"
        }
        response = self.client.put(f'/api/survey/{self.draft_survey.id}/condition/{self.draft_condition.id}/', data=data)
        self.assertEqual(response.status_code, 400)
        response = self.client.patch(f'/api/survey/{self.draft_survey.id}/condition/{self.draft_condition.id}/', data=data)
        self.assertEqual(response.status_code, 400)

        # invali source or target question id
        data = {
            "source_question": 999,
            "target_question": self.draft_question2.id,
            "condition": Condition.ConditionType.text_contain,
            "value": "10"
        }
        response = self.client.put(f'/api/survey/{self.draft_survey.id}/condition/{self.draft_condition.id}/', data=data)
        self.assertEqual(response.status_code, 400)
        response = self.client.patch(f'/api/survey/{self.draft_survey.id}/condition/{self.draft_condition.id}/', data=data)
        self.assertEqual(response.status_code, 400)

        data = {
            "source_question": self.draft_question1.id,
            "target_question": 999,
            "condition": Condition.ConditionType.text_contain,
            "value": "10"
        }
        response = self.client.put(f'/api/survey/{self.draft_survey.id}/condition/{self.draft_condition.id}/', data=data)
        self.assertEqual(response.status_code, 400)
        response = self.client.patch(f'/api/survey/{self.draft_survey.id}/condition/{self.draft_condition.id}/', data=data)
        self.assertEqual(response.status_code, 400)

        # invali value for any type of conditions
        # text type: blank
        data = {
            "source_question": self.draft_question1.id,
            "target_question": self.draft_question2.id,
            "condition": Condition.ConditionType.text_contain,
            "value": ""
        }
        response = self.client.put(f'/api/survey/{self.draft_survey.id}/condition/{self.draft_condition.id}/', data=data)
        self.assertEqual(response.status_code, 400)
        response = self.client.patch(f'/api/survey/{self.draft_survey.id}/condition/{self.draft_condition.id}/', data=data)
        self.assertEqual(response.status_code, 400)

        # number type: text
        number_question = Question.objects.create(
            title="q1",
            survey=self.draft_survey,
            question_type=Question.QuestionType.numerical,
            priority=1
        )
        data = {
            "source_question": number_question.id,
            "target_question": self.draft_question2.id,
            "condition": Condition.ConditionType.number_gt,
            "value": "asd"
        }
        response = self.client.put(f'/api/survey/{self.draft_survey.id}/condition/{self.draft_condition.id}/', data=data)
        self.assertEqual(response.status_code, 400)
        response = self.client.patch(f'/api/survey/{self.draft_survey.id}/condition/{self.draft_condition.id}/', data=data)
        self.assertEqual(response.status_code, 400)
        
        # option type: text - invalid id
        option_question = Question.objects.create(
            title="q1",
            survey=self.draft_survey,
            question_type=Question.QuestionType.option,
            priority=1
        )
        data = {
            "source_question": option_question.id,
            "target_question": self.draft_question2.id,
            "condition": Condition.ConditionType.option_equal,
            "value": "asd"
        }
        response = self.client.put(f'/api/survey/{self.draft_survey.id}/condition/{self.draft_condition.id}/', data=data)
        self.assertEqual(response.status_code, 400)
        response = self.client.patch(f'/api/survey/{self.draft_survey.id}/condition/{self.draft_condition.id}/', data=data)
        self.assertEqual(response.status_code, 400)

        # test OK
        response = self.client.put(f'/api/survey/{self.draft_survey.id}/condition/{self.draft_condition.id}/',
                                   data=draft_data)
        self.assertEqual(response.status_code, 200)
        response = self.client.patch(f'/api/survey/{self.draft_survey.id}/condition/{self.draft_condition.id}/',
                                     data=draft_data)
        self.assertEqual(response.status_code, 200)
    
    def test_delete_condition(self):
        # test invalid survey id
        response = self.client.delete('/api/survey/xxx/condition/xxx/')
        self.assertEqual(response.status_code, 404)
        response = self.client.delete('/api/survey/999/condition/999/')
        self.assertEqual(response.status_code, 404)

        # test invalid condition id
        response = self.client.delete(f'/api/survey/{self.draft_survey.id}/condition/xxx/')
        self.assertEqual(response.status_code, 404)
        response = self.client.delete(f'/api/survey/{self.draft_survey.id}/condition/999/')
        self.assertEqual(response.status_code, 404)

        # test delete condition that survey status is publish
        response = self.client.delete(f'/api/survey/{self.publish_survey.id}/condition/{self.publish_condition.id}/')
        self.assertEqual(response.status_code, 400)

        # test delete condition that not in survey
        response = self.client.delete(f'/api/survey/{self.draft_survey.id}/condition/{self.publish_condition.id}/')
        self.assertEqual(response.status_code, 404)

        # test ok
        response = self.client.delete(f'/api/survey/{self.draft_survey.id}/condition/{self.draft_condition.id}/')
        self.assertEqual(response.status_code, 204)


class TestOperatiorCRUD(APITestCase):
    def setUp(self):
        self.draft_survey = Survey.objects.create(title="s1")
        self.draft_question1 = Question.objects.create(
            title="q1",
            survey=self.draft_survey,
            question_type=Question.QuestionType.text,
            priority=1
        )
        self.draft_question2 = Question.objects.create(
            title="q2",
            survey=self.draft_survey,
            question_type=Question.QuestionType.text,
            priority=2
        )
        self.draft_condition1 = Condition.objects.create(
            survey=self.draft_survey,
            source_question=self.draft_question1,
            target_question=self.draft_question2,
            condition=Condition.ConditionType.text_contain,
            value="asd"
        )
        self.draft_condition2 = Condition.objects.create(
            survey=self.draft_survey,
            source_question=self.draft_question1,
            target_question=self.draft_question2,
            condition=Condition.ConditionType.text_contain,
            value="dsa"
        )
        self.draft_operator = Operatior.objects.create(
            first_condition=self.draft_condition1,
            second_condition=self.draft_condition2,
            operator=Operatior.OperatorType.and_operator,
            priority=1,
            survey=self.draft_survey,
        )

        self.publish_survey = Survey.objects.create(title="s1", status=Survey.StatusType.publish)
        self.publish_question1 = Question.objects.create(
            title="q1",
            survey=self.publish_survey,
            question_type=Question.QuestionType.text,
            priority=1
        )
        self.publish_question2 = Question.objects.create(
            title="q2",
            survey=self.publish_survey,
            question_type=Question.QuestionType.text,
            priority=2
        )
        self.publish_condition1 = Condition.objects.create(
            survey=self.publish_survey,
            source_question=self.publish_question1,
            target_question=self.publish_question2,
            condition=Condition.ConditionType.text_contain,
            value="asd"
        )
        self.publish_condition2 = Condition.objects.create(
            survey=self.publish_survey,
            source_question=self.publish_question1,
            target_question=self.publish_question2,
            condition=Condition.ConditionType.text_contain,
            value="dsa"
        )
        self.publish_operator = Operatior.objects.create(
            first_condition=self.publish_condition1,
            second_condition=self.publish_condition2,
            operator=Operatior.OperatorType.and_operator,
            priority=1,
            survey=self.publish_survey,
        )
    
    def test_list_operatior(self):
        # test invalid survey id
        response = self.client.get(f'/api/survey/xxx/condition/operator/')
        self.assertEqual(response.status_code, 404)
        response = self.client.get(f'/api/survey/999/condition/operator/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

        # test list draft/publish survey
        response = self.client.get(f'/api/survey/{self.draft_survey.id}/condition/operator/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        response = self.client.get(f'/api/survey/{self.publish_survey.id}/condition/operator/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
    
    def test_retrive_operatior(self):
        # test invalid survey_id and condition_id
        response = self.client.get(f'/api/survey/xxx/condition/operator/xxx/')
        self.assertEqual(response.status_code, 404)
        response = self.client.get(f'/api/survey/999/condition/operator/999/')
        self.assertEqual(response.status_code, 404)

        # test list draft/publish survey
        response = self.client.get(f'/api/survey/{self.draft_survey.id}/condition/operator/{self.draft_operator.id}/')
        response_data = response.json()
        self.assertEqual(response.status_code, 200)
        # self.assertEqual(response_data["id"], self.draft_condition.id)
        # self.assertEqual(response_data["source_question"], self.draft_condition.source_question.id)
        # self.assertEqual(response_data["target_question"], self.draft_condition.target_question.id)
        # self.assertEqual(response_data["condition"], self.draft_condition.condition)
        # self.assertEqual(response_data["value"], self.draft_condition.value)
        response = self.client.get(f'/api/survey/{self.publish_survey.id}/condition/operator/{self.publish_operator.id}/')
        response_data = response.json()
        self.assertEqual(response.status_code, 200)
        # self.assertEqual(response_data["id"], self.publish_condition.id)
        # self.assertEqual(response_data["source_question"], self.publish_condition.source_question.id)
        # self.assertEqual(response_data["target_question"], self.publish_condition.target_question.id)
        # self.assertEqual(response_data["condition"], self.publish_condition.condition)
        # self.assertEqual(response_data["value"], self.publish_condition.value)

    def test_create_operatior(self):
        return
        
    def test_update_operatior(self):
        return
    
    def test_delete_operatior(self):
        return
