from odoo.exceptions import AccessError
from odoo.tests.common import TransactionCase, tagged
from .common import Common


@tagged('post_install', '-at_install')
class TestAccessRight(Common):

    def test_access_right_survey_question_bank_category(self):
        survey_question_bank_category = self.env['survey.question.bank.category'].with_user(self.survey_exam_manager).create({
            'name': 'Python'
        })
        survey_question_bank_category.with_user(self.survey_exam_manager).read(['name'])
        survey_question_bank_category.with_user(self.survey_exam_manager).name = 'Python 2'
        survey_question_bank_category.with_user(self.survey_exam_manager).unlink()

        with self.assertRaises(AccessError):
            self.env['survey.question.bank.category'].with_user(self.user_1).create({
                'name': 'Python 3'
            })
        with self.assertRaises(AccessError):
            survey_question_bank_category.with_user(self.user_1).read(['name'])
        with self.assertRaises(AccessError):
            survey_question_bank_category.with_user(self.user_1).name = 'Python 3'
        with self.assertRaises(AccessError):
            survey_question_bank_category.with_user(self.user_1).unlink()

    def test_access_right_survey_question_bank_answer(self):
        survey_question_bank_answer = self.env['survey.question.bank.answer'].with_user(self.survey_exam_manager).create({
            'value': '1'
        })
        survey_question_bank_answer.with_user(self.survey_exam_manager).read(['value'])
        survey_question_bank_answer.with_user(self.survey_exam_manager).value = '2'
        survey_question_bank_answer.with_user(self.survey_exam_manager).unlink()

        with self.assertRaises(AccessError):
            self.env['survey.question.bank.answer'].with_user(self.user_1).create({
                'value': '2'
            })
        with self.assertRaises(AccessError):
            survey_question_bank_answer.with_user(self.user_1).read(['value'])
        with self.assertRaises(AccessError):
            survey_question_bank_answer.with_user(self.user_1).value = '3'
        with self.assertRaises(AccessError):
            survey_question_bank_answer.with_user(self.user_1).unlink()

    def test_access_right_survey_question_bank(self):
        survey_question_bank = self.env['survey.question.bank'].with_user(self.survey_exam_manager).create({
            'name': 'test 1',
            'category_id': self.survey_question_bank_category_2.id,
        })
        survey_question_bank.with_user(self.survey_exam_manager).read(['name'])
        survey_question_bank.with_user(self.survey_exam_manager).name = 'test 2'
        survey_question_bank.with_user(self.survey_exam_manager).unlink()

        with self.assertRaises(AccessError):
            self.env['survey.question.bank'].with_user(self.user_1).create({
                'name': 'test 2',
                'category_id': self.survey_question_bank_category_2.id
            })
        with self.assertRaises(AccessError):
            survey_question_bank.with_user(self.user_1).read(['name'])
        with self.assertRaises(AccessError):
            survey_question_bank.with_user(self.user_1).name = 'test 3'
        with self.assertRaises(AccessError):
            survey_question_bank.with_user(self.user_1).unlink()
