from odoo.tests.common import SavepointCase


class Common(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(Common, cls).setUpClass()
        cls.user_1 = cls.env['res.users'].create({
            'name': 'user test 1',
            'login': 'user test 1',
            'groups_id': [(6, 0, cls.env.ref('base.group_user').ids)],
            'email': 'user1test@example.viindoo.com'
        })
        cls.survey_exam_manager = cls.env['res.users'].create({
            'name': 'survey exam manager',
            'login': 'survey exam manager',
            'groups_id': [(6, 0, [cls.env.ref('viin_survey_exam.survey_exam_group_manager').id])],
            'email': 'user2test@example.viindoo.com'
        })

        cls.survey_question_bank_category_1 = cls.env['survey.question.bank.category'].create({
            'name': 'Python'
        })
        cls.survey_question_bank_category_2 = cls.env['survey.question.bank.category'].create({
            'name': 'Python 3.7'
        })
        cls.survey_question_bank_1 = cls.env['survey.question.bank'].create({
            'name': 'test survey question bank 1',
            'category_id': cls.survey_question_bank_category_1.id,
            'description': 'desc test'
        })

        cls.answer_1 = cls.env['survey.question.bank.answer'].create({
            'value': '1',
            'question_id': cls.survey_question_bank_1.id
        })
        cls.answer_2 = cls.env['survey.question.bank.answer'].create({
            'value': '2',
            'question_id': cls.survey_question_bank_1.id,
            'is_correct': True
        })
        cls.answer_3 = cls.env['survey.question.bank.answer'].create({
            'value': '0',
            'question_id': cls.survey_question_bank_1.id
        })
        cls.answer_4 = cls.env['survey.question.bank.answer'].create({
            'value': '4',
            'question_id': cls.survey_question_bank_1.id
        })

        cls.survey_1 = cls.env['survey.survey'].create({
            'title': 'Survey Test'
        })

        cls.image1_base64 = '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'
