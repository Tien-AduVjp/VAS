from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestViinSurveyExam(TransactionCase):

    def setUp(self):
        super(TestViinSurveyExam, self).setUp()
        self.survey_question_bank_category_1 = self.env['survey.question.bank.category'].create({
            'name': 'Python'
        })
        self.survey_question_bank_category_2 = self.env['survey.question.bank.category'].create({
            'name': 'Python 3.7'
        })
        self.survey_question_bank_1 = self.env['survey.question.bank'].create({
            'name': 'test survey question bank 1',
            'category_id': self.survey_question_bank_category_1.id,
            'description': 'desc test'
        })

        self.answer_1 = self.env['survey.question.bank.answer'].create({
            'value': '1',
            'question_id': self.survey_question_bank_1.id
        })
        self.answer_2 = self.env['survey.question.bank.answer'].create({
            'value': '2',
            'question_id': self.survey_question_bank_1.id,
            'is_correct': True
        })
        self.answer_3 = self.env['survey.question.bank.answer'].create({
            'value': '0',
            'question_id': self.survey_question_bank_1.id
        })
        self.answer_4 = self.env['survey.question.bank.answer'].create({
            'value': '4',
            'question_id': self.survey_question_bank_1.id
        })

        self.survey_1 = self.env['survey.survey'].create({
            'title': 'Survey Test'
        })

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
        self.assertEqual(self.survey_question_bank_1.display_mode, question_1.display_mode)
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
            'question_type': 'free_text',
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
