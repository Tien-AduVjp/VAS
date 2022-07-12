from odoo import models, _


class MailActivity(models.Model):
    _inherit = 'mail.activity'

    def _action_done(self, feedback=False, attachment_ids=None):
        employee_activities = self.filtered(lambda act: act.res_model == 'hr.employee')
        if employee_activities:
            messages, next_activities = super(MailActivity, self.sudo())._action_done(feedback, attachment_ids)
            messages.copy(default={
                'model': 'hr.employee.public',
            })
            return messages, next_activities
        return super(MailActivity, self)._action_done(feedback, attachment_ids)

    def unlink(self):
        for r in self.filtered(lambda r: r.res_model == 'hr.employee.public'):
            msg = self.env['ir.translation']._get_source(None, ('code',), self.env.user.lang, _('To Do canceled (originally assigned to %s): %s'))
            self.env[r.res_model].browse(r.res_id).message_post(body=msg % (r.user_id.name, r.summary))
        return super(MailActivity, self).unlink()

    # Reload page
    def action_close_dialog(self):
        if self.env.context.get('default_res_model') == 'hr.employee.public':
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }
        return super(MailActivity, self).action_close_dialog()
