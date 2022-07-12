from odoo import models

class SurveyUserInputLine(models.Model):
    _inherit = 'survey.user_input.line'

    def _recompute_answer_score(self):
        for r in self:
            if r.suggested_answer_id:
                r.write({
                    'answer_is_correct': r.suggested_answer_id.is_correct,
                    'answer_score': r.suggested_answer_id.answer_score
                })
