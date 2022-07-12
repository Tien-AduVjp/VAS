from odoo import models

class Survey(models.Model):
    _inherit = 'survey.survey'
    
    def action_recompute_answer_score(self):
        self.mapped('user_input_ids.user_input_line_ids')._recompute_answer_score()
