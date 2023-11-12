from rest_framework.test import APITestCase

from survey.models import Survey, Question, Option, Condition


class TestQuestionCRUD(APITestCase):
    def setUp(self):
        self.draft_survey = Survey.objects.create(title="default publish survey")
        self.publish_survey = Survey.objects.create(title="default publish survey", status=Survey.StatusType.publish)
        self.draft_question = Question.objects.create(
            title="q1",
            survey=self.draft_survey,
            question_type=Question.QuestionType.text,
            priority=1
        )
        self.publish_question = Question.objects.create(
            title="q1",
            survey=self.publish_survey,
            question_type=Question.QuestionType.text,
            priority=1
        )
        
    def test_create_question(self):
        data = {
            "title": "title",
            "question_type": Question.QuestionType.text,
            "priority": 0
        }
        response = self.client.post('/api/survey/xxx/question/', data=data)
        self.assertEqual(response.status_code, 404)
        response = self.client.post('/api/survey/999/question/', data=data)
        self.assertEqual(response.status_code, 404)
        response = self.client.post(f'/api/survey/{self.publish_survey.id}/question/', data=data)
        self.assertEqual(response.status_code, 400)
        response = self.client.post(f'/api/survey/{self.draft_survey.id}/question/', data=data)
        self.assertEqual(response.status_code, 201)
    
    def test_list_question(self):
        response = self.client.get(f'/api/survey/xxx/question/')
        self.assertEqual(response.status_code, 404)
        response = self.client.get(f'/api/survey/999/question/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])
        response = self.client.get(f'/api/survey/{self.draft_survey.id}/question/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        response = self.client.get(f'/api/survey/{self.publish_survey.id}/question/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
    
    def test_retrive_question(self):
        response = self.client.get(f'/api/survey/xxx/question/xxx/')
        self.assertEqual(response.status_code, 404)
        response = self.client.get('/api/survey/999/question/999/')
        self.assertEqual(response.status_code, 404)
        response = self.client.get(f'/api/survey/{self.draft_survey.id}/question/{self.draft_question.id}/')
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data["id"], self.draft_question.id)
        self.assertEqual(response_data["title"], self.draft_question.title)
        self.assertEqual(response_data["question_type"], self.draft_question.question_type)
        self.assertEqual(response_data["required"], self.draft_question.required)
        self.assertEqual(response_data["priority"], self.draft_question.priority)
        self.assertEqual(response_data["options"], None)
        response = self.client.get(f'/api/survey/{self.publish_survey.id}/question/{self.publish_question.id}/')
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data["id"], self.publish_question.id)
        self.assertEqual(response_data["title"], self.publish_question.title)
        self.assertEqual(response_data["question_type"], self.publish_question.question_type)
        self.assertEqual(response_data["required"], self.publish_question.required)
        self.assertEqual(response_data["priority"], self.publish_question.priority)
        self.assertEqual(response_data["options"], None)
    
    def test_update_question(self):
        response = self.client.put(f'/api/survey/xxx/question/xxx/')
        self.assertEqual(response.status_code, 404)
        response = self.client.patch(f'/api/survey/xxx/question/xxx/')
        self.assertEqual(response.status_code, 404)
        response = self.client.put('/api/survey/999/question/999/')
        self.assertEqual(response.status_code, 404)
        response = self.client.patch('/api/survey/999/question/999/')
        self.assertEqual(response.status_code, 404)
        question_data = {
            "title": "title",
            "question_type": Question.QuestionType.numerical,
            "required": True,
            "priority": 69
        }
        response = self.client.put(
            f'/api/survey/{self.publish_survey.id}/question/{self.publish_question.id}/', data=question_data)
        self.assertEqual(response.status_code, 400)
        response = self.client.put(
            f'/api/survey/{self.draft_survey.id}/question/{self.draft_question.id}/', data=question_data)
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data["id"], self.draft_question.id)
        self.assertEqual(response_data["title"], question_data["title"])
        self.assertEqual(response_data["question_type"], question_data["question_type"])
        self.assertEqual(response_data["required"], question_data["required"])
        self.assertEqual(response_data["priority"], question_data["priority"])
        # test change question type and check related options and conditions
        sample_condition = Condition.objects.create(
            survey=self.draft_survey,
            source_question=self.draft_question,
            target_question=self.draft_question,
            condition=Condition.ConditionType.text_contain,
            value="XxXxXxXx"
        )
        sample_condition_id = sample_condition.id
        sample_option = Option.objects.create(title="option", question=self.draft_question, priority=1)
        sample_option_id = sample_option.id
        response = self.client.patch(
            f'/api/survey/{self.draft_survey.id}/question/{self.draft_question.id}/',
            data={"question_type": Question.QuestionType.option})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Condition.objects.filter(id=sample_condition_id).exists(), False)
        self.assertEqual(Option.objects.filter(id=sample_option_id).exists(), False)
    
    def test_delete_question(self):
        response = self.client.delete(f'/api/survey/xxx/question/xxx/')
        self.assertEqual(response.status_code, 404)
        response = self.client.delete('/api/survey/999/question/999/')
        self.assertEqual(response.status_code, 404)
        response = self.client.delete(f'/api/survey/{self.draft_survey.id}/question/{self.draft_question.id}/')
        self.assertEqual(response.status_code, 204)
        response = self.client.get(f'/api/survey/{self.publish_survey.id}/question/{self.publish_question.id}/')
        self.assertEqual(response.status_code, 200)
        response = self.client.delete(f'/api/survey/{self.publish_survey.id}/')
        self.assertEqual(response.status_code, 400)


class TestFirstQuestion(APITestCase):
    def test_first_question(self):
        response = self.client.get('/api/survey/xxx/question/first_question')
        self.assertEqual(response.status_code, 404)
        response = self.client.get('/api/survey/999/question/first_question')
        self.assertEqual(response.status_code, 404)

        empty_survey = Survey.objects.create(title="empty", status=Survey.StatusType.publish)
        response = self.client.get(f'/api/survey/{empty_survey.id}/question/first_question')
        self.assertEqual(response.status_code, 404)

        survey_1 = Survey.objects.create(title="s1", status=Survey.StatusType.draft)
        Question.objects.create(
            title="q1",
            survey=survey_1,
            question_type=Question.QuestionType.text,
            priority=2
        )
        first_question = Question.objects.create(
            title="q2",
            survey=survey_1,
            question_type=Question.QuestionType.text,
            priority=1
        )
        response = self.client.get(f'/api/survey/{survey_1.id}/question/first_question')
        self.assertEqual(response.status_code, 404)

        survey_1.status = Survey.StatusType.publish
        survey_1.save()
        response = self.client.get(f'/api/survey/{survey_1.id}/question/first_question')
        response_data = response.json()
        self.assertEqual(response_data["id"], first_question.id)
        self.assertEqual(response_data["title"], first_question.title)
        self.assertEqual(response_data["question_type"], first_question.question_type)
        self.assertEqual(response_data["required"], first_question.required)
        self.assertEqual(response_data["priority"], first_question.priority)


class TestOptionCRUD(APITestCase):
    def setUp(self):    
        self.draft_survey = Survey.objects.create(title="default publish survey")
        self.draft_option_question = Question.objects.create(
            title="q1",
            survey=self.draft_survey,
            question_type=Question.QuestionType.option,
            priority=1
        )
        self.draft_text_question = Question.objects.create(
            title="q2",
            survey=self.draft_survey,
            question_type=Question.QuestionType.text,
            priority=2
        )
        self.draft_option = Option.objects.create(
            title="o1",
            question=self.draft_option_question,
            priority=1
        )
        Condition.objects.create(
            survey=self.draft_survey,
            source_question=self.draft_option_question,
            target_question=self.draft_text_question,
            condition=Condition.ConditionType.option_equal,
            value=self.draft_option.id
        )

        self.publish_survey = Survey.objects.create(title="default publish survey", status=Survey.StatusType.publish)
        self.publish_option_question = Question.objects.create(
            title="q1",
            survey=self.publish_survey,
            question_type=Question.QuestionType.option,
            priority=2
        )
        self.publish_option = Option.objects.create(
            title="o1",
            question=self.publish_option_question,
            priority=1
        )

    def test_list_option(self):
        response = self.client.get(f'/api/survey/question/{self.publish_option_question.id}/option/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        
    def test_retrive_option(self):
        response = self.client.get('/api/survey/question/xxx/option/xxx/')
        self.assertEqual(response.status_code, 404)
        response = self.client.get('/api/survey/question/999/option/999/')
        self.assertEqual(response.status_code, 404)
        response = self.client.get(
            f'/api/survey/question/{self.publish_option_question.id}/option/{self.publish_option.id}/')
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data["id"], self.publish_option.id)
        self.assertEqual(response_data["title"], self.publish_option.title)
        self.assertEqual(response_data["priority"], self.publish_option.priority)
    
    def test_create_option(self):
        data = {
            "title": "title",
            "priority": 0
        }
        response = self.client.post(f'/api/survey/question/xxx/option/', data=data)
        self.assertEqual(response.status_code, 404)
        response = self.client.post('/api/survey/question/999/option/', data=data)
        self.assertEqual(response.status_code, 400)
        response = self.client.post(f'/api/survey/question/{self.publish_option_question.id}/option/', data=data)
        self.assertEqual(response.status_code, 400)
        response = self.client.post(f'/api/survey/question/{self.draft_text_question.id}/option/', data=data)
        self.assertEqual(response.status_code, 400)
        response = self.client.post(f'/api/survey/question/{self.draft_option_question.id}/option/', data=data)
        self.assertEqual(response.status_code, 201)
    
    def test_update_option(self):
        data = {
            "title": "title-2",
            "priority": 1
        }
        response = self.client.put(f'/api/survey/question/xxx/option/xxx/', data=data)
        self.assertEqual(response.status_code, 404)
        response = self.client.patch(f'/api/survey/question/xxx/option/xxx/', data=data)
        self.assertEqual(response.status_code, 404)
        response = self.client.put('/api/survey/question/999/option/999/', data=data)
        self.assertEqual(response.status_code, 404)
        response = self.client.patch('/api/survey/question/999/option/999/', data=data)
        self.assertEqual(response.status_code, 404)
        response = self.client.put(
            f'/api/survey/question/{self.publish_option_question.id}/option/{self.publish_option.id}/', data=data)
        self.assertEqual(response.status_code, 400)
        response = self.client.patch(
            f'/api/survey/question/{self.publish_option_question.id}/option/{self.publish_option.id}/', data=data)
        self.assertEqual(response.status_code, 400)
        response = self.client.put(
            f'/api/survey/question/{self.draft_option_question.id}/option/{self.draft_option.id}/', data=data)
        response_data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data["title"], data["title"])
        self.assertEqual(response_data["priority"], data["priority"])
    
    def test_delete_option(self):
        response = self.client.delete(f'/api/survey/question/xxx/option/xxx/')
        self.assertEqual(response.status_code, 404)
        response = self.client.delete('/api/survey/question/999/option/999/')
        self.assertEqual(response.status_code, 404)
        response = self.client.delete(
            f'/api/survey/question/{self.publish_option_question.id}/option/{self.publish_option.id}/')
        self.assertEqual(response.status_code, 400)

        response = self.client.delete(
            f'/api/survey/question/{self.draft_option_question.id}/option/{self.draft_option.id}/')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Condition.objects.filter(value=self.draft_option.id).exists(), False)
