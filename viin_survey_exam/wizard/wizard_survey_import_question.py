from odoo import fields, models

class WizardSurveyImportQuestion(models.TransientModel):
    _name = 'survey.import.question.wizard'
    _description = 'Wizard Survey Import from Questions Bank'

    survey_id = fields.Many2one('survey.survey', string="Survey", required=True)
    question_ids = fields.Many2many('survey.question.bank', string="Questions Bank")

    def action_import(self):
        self.ensure_one()
        return self.survey_id.import_question_from_question_bank(self.question_ids)
