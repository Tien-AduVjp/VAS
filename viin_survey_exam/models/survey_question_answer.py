from odoo import models


class SurveyQuestionAnswer(models.Model):
    _inherit = 'survey.question.answer'

    def _prepare_answer_value(self):
        self.ensure_one()
        return {
            'sequence': self.sequence,
            'value': self.value,
            'is_correct': self.is_correct,
            'answer_score': self.answer_score,
            'value_image': self.value_image
        }
