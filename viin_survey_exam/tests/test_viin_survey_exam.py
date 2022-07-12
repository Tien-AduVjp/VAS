from odoo.exceptions import UserError
from odoo.tests.common import tagged
from odoo.tools import image_process

from .common import Common


@tagged('post_install', '-at_install')
class TestViinSurveyExam(Common):

    def test_create_survey_question_bank_category(self):
        # case 1.1:
        with self.assertRaises(UserError):
            self.survey_question_bank_category_1.parent_id = self.survey_question_bank_category_1

        # case 1.2:
        self.survey_question_bank_category_2.parent_id = self.survey_question_bank_category_1
        with self.assertRaises(UserError):
            self.survey_question_bank_category_1.parent_id = self.survey_question_bank_category_2

        # case 1.3:
        self.survey_question_bank_category_2.parent_id = self.survey_question_bank_category_1

    def test_import_question_from_question_bank(self):
        # case 3:
        self.survey_1.import_question_from_question_bank(self.survey_question_bank_1)
        question_1 = self.survey_1.question_ids

        self.assertEqual(self.survey_question_bank_1.name, question_1.title)
        self.assertEqual(self.survey_question_bank_1.description, question_1.description)

        self.assertEqual(self.survey_question_bank_1.constr_mandatory, question_1.constr_mandatory)
        self.assertEqual(self.survey_question_bank_1.constr_error_msg, question_1.constr_error_msg)

        self.assertEqual(self.survey_question_bank_1.column_nb, question_1.column_nb)
        self.assertEqual(self.survey_question_bank_1.comments_allowed, question_1.comments_allowed)

    def test_compute_question_count(self):
        # case 6:
        self.assertEqual(self.survey_question_bank_category_1.question_count, 1)
        self.assertEqual(self.survey_question_bank_category_2.question_count, 0)

        self.survey_question_bank_1.category_id = self.survey_question_bank_category_2
        self.survey_question_bank_category_2._compute_question_count()
        self.assertEqual(self.survey_question_bank_category_2.question_count, 1)

    def test_generate_questions_bank_from_suvey_questions(self):
        # case 9:
        survey_question_1 = self.env['survey.question'].create({
            'title': '(test) 1 - 1 =?',
            'question_type': 'simple_choice',
            'survey_id': self.survey_1.id
        })
        survey_question_2 = self.env['survey.question'].create({
            'title': '(test) 1 - 2 =?',
            'question_type': 'multiple_choice',
            'survey_id': self.survey_1.id
        })
        survey_question_3 = self.env['survey.question'].create({
            'title': '(test) 1 + 2 =?',
            'question_type': 'text_box',
            'survey_id': self.survey_1.id
        })

        survey_question_1.create_question_bank(self.survey_question_bank_category_1)
        survey_question_bank = self.env['survey.question.bank'].search([('name', '=', '(test) 1 - 1 =?')], limit=1)
        self.assertTrue(bool(survey_question_bank))

        survey_question_2.create_question_bank(self.survey_question_bank_category_1)
        survey_question_bank = self.env['survey.question.bank'].search([('name', '=', '(test) 1 - 2 =?')], limit=1)
        self.assertTrue(bool(survey_question_bank))

        with self.assertRaises(UserError):
            survey_question_3.create_question_bank(self.survey_question_bank_category_1)

    def test_01_data_sync(self):
        """ Test question data sync when import question from question bank:
                - Images on answers, Live  Session
        """
        self.survey_question_bank_1.write({
            'allow_value_image': True,
            'is_time_limited': True,
            'time_limit': 123,
            'answer_ids': False
        })
        question_bank_anwser = self.env['survey.question.bank.answer'].create({
            'value': 'Anwser 1',
            'value_image': self.image1_base64,
            'question_id': self.survey_question_bank_1.id
        })

        self.survey_1.import_question_from_question_bank(self.survey_question_bank_1)
        question = self.survey_1.question_ids

        self.assertEqual(question.allow_value_image, True)
        self.assertEqual(question.is_time_limited, True)
        self.assertEqual(question.time_limit, 123)

        self.assertEqual(question.suggested_answer_ids.value, 'Anwser 1')
        self.assertEqual(
            question.suggested_answer_ids.value_image,
            image_process(self.image1_base64, size=(256, 256), verify_resolution=True)
        )

    def test_02_data_sync(self):
        """ Test question data sync when generate questions bank from survey questions:
                - Images on answers, Live  Session
        """
        survey_question_1 = self.env['survey.question'].create({
            'title': 'Survey Question 1',
            'question_type': 'multiple_choice',
            'survey_id': self.survey_1.id,
            'allow_value_image': True,
            'is_time_limited': True,
            'time_limit': 222,
        })
        answer1 = self.env['survey.question.answer'].create({
            'value': 'answer 1',
            'question_id': survey_question_1.id,
            'value_image': self.image1_base64,
        })

        survey_question_1.create_question_bank(self.survey_question_bank_category_1)
        survey_question_bank = self.env['survey.question.bank'].search([
            ('name', '=', 'Survey Question 1'),
            ('allow_value_image', '=', True),
            ('is_time_limited', '=', True),
            ('time_limit', '=', 222)
        ], limit=1)

        self.assertTrue(survey_question_bank)

        self.assertEqual(survey_question_bank.answer_ids.value, 'answer 1')
        self.assertEqual(
            survey_question_bank.answer_ids.value_image,
            image_process(self.image1_base64, size=(256, 256), verify_resolution=True)
        )
