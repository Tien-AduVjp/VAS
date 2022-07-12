from odoo import models, fields


class MailActivity(models.Model):
    _inherit = 'mail.activity'
    
    employee_resign_id = fields.Many2one('hr.employee.resignation', string="Employee Resign")
    
    def _action_done(self, feedback=False, attachment_ids=None):
        employee_resigns = self.employee_resign_id
        res = super(MailActivity, self)._action_done(feedback, attachment_ids)
        for employee_resign in employee_resigns:
            activities = self.env['mail.activity'].search([('employee_resign_id', '=', employee_resign.id)])
            if not activities:
                employee_resign.action_done()
        return res
