from odoo import fields, models


class SurveyQuestionBankAnswer(models.Model):
    _name = 'survey.question.bank.answer'
    _description = 'Answers for questions bank'
    
    question_id = fields.Many2one('survey.question.bank', string="Question")
    sequence = fields.Integer('Sequence order', default=10)
    value = fields.Char('Answer value', translate=True, required=True)
    is_correct = fields.Boolean('Is a correct answer')
    answer_score = fields.Float('Score for this choice', 
        help="A positive score indicates a correct choice; a negative or null score indicates a wrong answer")

    def _prepare_answer_value(self):
        self.ensure_one()
        return {
            'sequence': self.sequence,
            'value': self.value,
            'is_correct': self.is_correct,
            'answer_score': self.answer_score,
        }
