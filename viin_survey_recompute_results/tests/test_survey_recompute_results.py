from odoo.tests.common import SavepointCase, Form, tagged


@tagged('post_install', '-at_install')
class TestSurveyRecomputeResults(SavepointCase):

    def setUp(self):
        super(TestSurveyRecomputeResults, self).setUp()
        self.survey1 = self.env['survey.survey'].create({'title': 'Test 1'})

        self.question1 = self.env['survey.question'].create({
            'title': '1 + 1 =?',
            'question_type': 'simple_choice',
            'suggested_answer_ids': [
                (0, 0, {'value': '1'}),
                (0, 0, {'value': '2'}),
                (0, 0, {'value': '3', 'is_correct': True, 'answer_score': 1}),
                (0, 0, {'value': '4'})
            ],
            'survey_id': self.survey1.id
        })
        self.survey_userinput1 = self.env['survey.user_input'].create({
            'survey_id': self.survey1.id,
            'predefined_question_ids': [(6, 0, self.question1.ids)],
            'user_input_line_ids': [
                (0, 0, {
                    'question_id': self.question1.id,
                    'answer_type': 'suggestion',
                    'suggested_answer_id': self.question1.suggested_answer_ids[1].id
                })
            ],
            'state': 'done'
        })

    def test_recompute_results(self):
        # case 1:
        self.assertEqual(self.survey_userinput1.scoring_percentage, 0)

        self.question1.suggested_answer_ids[2].write({
            'is_correct': False,
            'answer_score': 0
        })
        self.question1.suggested_answer_ids[1].write({
            'is_correct': True,
            'answer_score': 1
        })

        self.survey1.action_recompute_answer_score()
        self.assertEqual(self.survey_userinput1.scoring_percentage, 100)
