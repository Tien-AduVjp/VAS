from odoo import api, models


class QualityAlertPreventiveAction(models.Model):
    _name = 'quality.alert.preventive.action'
    _description = 'Preventive Quality Alert Action'
    _inherits = {'quality.alert.action': 'alert_action_id'}
    _inherit = ['abstract.quality.alert.action']
    _mail_post_access = 'read'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['type'] = 'preventive'
        return super(QualityAlertPreventiveAction, self).create(vals_list)
