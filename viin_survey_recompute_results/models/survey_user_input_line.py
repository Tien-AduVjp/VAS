from odoo import models

class SurveyUserInputLine(models.Model):
    _inherit = 'survey.user_input_line'
    
    def _recompute_answer_score(self):
        for r in self:
            if r.value_suggested:
                r.answer_score = r.value_suggested.answer_score
