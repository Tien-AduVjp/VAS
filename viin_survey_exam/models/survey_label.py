from odoo import models


class SurveyLabel(models.Model):
    _inherit = 'survey.label'
    
    def _prepare_answer_value(self):
        self.ensure_one()
        return {
            'sequence': self.sequence,
            'value': self.value,
            'is_correct': self.is_correct,
            'answer_score': self.answer_score,
        }
