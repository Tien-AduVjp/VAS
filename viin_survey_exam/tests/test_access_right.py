from odoo.exceptions import AccessError
from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestAccessRight(TransactionCase):

    def setUp(self):
        super(TestAccessRight, self).setUp()
        self.user_1 = self.env['res.users'].create({
            'name': 'user test 1',
            'login': 'user test 1',
            'groups_id': [(6, 0, self.env.ref('base.group_user').ids)],
            'email': 'user1test@example.viindoo.com'
        })
        self.survey_exam_manager = self.env['res.users'].create({
            'name': 'survey exam manager',
            'login': 'survey exam manager',
            'groups_id': [(6, 0, [self.env.ref('viin_survey_exam.survey_exam_group_manager').id,
                                  self.env.ref('base.group_user').id])],
            'email': 'user2test@example.viindoo.com'
        })
        self.survey_question_bank_category_2 = self.env['survey.question.bank.category'].create({
            'name': 'Python 3.7'
        })

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
