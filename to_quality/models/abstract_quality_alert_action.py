from odoo import api, fields, models


class AbstractQualityAlertAction(models.AbstractModel):
    _name = 'abstract.quality.alert.action'
    _description = 'Abstract Quality Alert Action to share business logics'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'alert_action_id'

    alert_action_id = fields.Many2one('quality.alert.action', string='Quality Alert Action', required=True, ondelete="cascade", index=True)

    @api.model_create_multi
    def create(self, vals_list):
        records = super(AbstractQualityAlertAction, self).create(vals_list)
        records.alert_action_id._compute_user_id()
        records.alert_action_id._compute_description()
        return records

    def unlink(self):
        alert_actions = self.mapped('alert_action_id')
        res = super(AbstractQualityAlertAction, self).unlink()
        alert_actions.unlink()
        return res
