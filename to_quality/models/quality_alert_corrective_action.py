from odoo import api, models


class QualityAlertCorrectiveAction(models.Model):
    _name = 'quality.alert.corrective.action'
    _description = 'Corrective Quality Alert Action'
    _inherits = {'quality.alert.action': 'alert_action_id'}
    _inherit = ['abstract.quality.alert.action']
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['type'] = 'corrective'
        return super(QualityAlertCorrectiveAction, self).create(vals_list)
