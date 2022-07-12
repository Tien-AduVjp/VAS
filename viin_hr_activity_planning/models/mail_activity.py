from odoo import models


class MailActivity(models.Model):
    _inherit = 'mail.activity'

    def _action_done(self, feedback=False, attachment_ids=None):
        employee_activities = self.filtered(lambda act: act.res_model_id == self.env['ir.model']._get('hr.employee'))
        if employee_activities:
            self = self.sudo()
            messages, next_activities = super(MailActivity, self)._action_done(feedback, attachment_ids)
            messages.copy(default={
                'model': 'hr.employee.public',
            })
            return messages, next_activities
        return super(MailActivity, self)._action_done(feedback, attachment_ids)
