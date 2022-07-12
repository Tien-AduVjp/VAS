from odoo import api, models


class Task(models.Model):
    _inherit = 'project.task'

    def _track_subtype(self, init_values):
        if not self.project_id.kanban_state_notification:
            return None
        if 'kanban_state_label' in init_values and self.kanban_state == 'normal':
            return self.env.ref('viin_project_kanban_state_notification.mt_task_return')
        else:
            return super(Task, self)._track_subtype(init_values)

    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, **kwargs):
        # OVERRIDE
        self.ensure_one()
        trackings = kwargs.get('tracking_value_ids', [])
        partner = self.project_id.sudo().user_id.partner_id
        if partner and self.project_id.sudo().user_id != self.env.user:
            kanban_state_label_field = self.env['ir.model.fields']._get('project.task', 'kanban_state_label')
            for tracking in trackings:
                if tracking[-1]['field'] == kanban_state_label_field.id:
                    kwargs['partner_ids'] = kwargs.get('partner_ids', []) + [partner.id]
                    kwargs['body'] = kwargs.get('body',
                                                '') + '<a href="#" class="o_mail_redirect" data-oe-id="%s" data-oe-model="res.partner" target="_blank">@%s</a>' % (
                                     partner.id, partner.name)
        return super(Task, self).message_post(**kwargs)
