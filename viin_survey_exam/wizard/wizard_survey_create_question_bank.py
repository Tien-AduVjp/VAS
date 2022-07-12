from odoo import fields, models

class WizardSurveyCreateQuestionBank(models.TransientModel):
    _name = 'survey.create.question.bank.wizard'
    _description = 'Wizard Survey Create Questions Bank'
    
    category_id = fields.Many2one('survey.question.bank.category', string="Category", required=True)
    
    def action_create_question(self):
        self.ensure_one()
        active_ids = self._context.get('active_ids', [])
        if active_ids:
            questions = self.env['survey.question'].browse(active_ids)
            if questions.exists():
                questions.create_question_bank(self.category_id)
                action = self.env.ref('viin_survey_exam.survey_question_bank_action').read()[0]
                return action
        return True
