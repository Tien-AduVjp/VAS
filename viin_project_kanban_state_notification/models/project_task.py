from odoo import api, models


class Task(models.Model):
    _inherit = 'project.task'

    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, **kwargs):
        # OVERRIDE
        self.ensure_one()
        trackings = kwargs.get('tracking_value_ids', [])
        partner = self.project_id.user_id.partner_id
        if partner and self.project_id.user_id != self.env.user:
            for tracking in trackings:
                if tracking[-1]['field'] == 'kanban_state_label':
                    kwargs['partner_ids'] = kwargs.get('partner_ids', []) + [partner.id]
                    kwargs['body'] = kwargs.get('body',
                                                '') + '<a href="#" class="o_mail_redirect" data-oe-id="%s" data-oe-model="res.partner" target="_blank">@%s</a>' % (
                                     partner.id, partner.name)
        return super(Task, self).message_post(**kwargs)
