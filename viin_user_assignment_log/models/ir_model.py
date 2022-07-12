from odoo import models, fields, api
from odoo import tools
from odoo.tools.sql import column_exists


class IrModel(models.Model):
    _inherit = 'ir.model'

    def __init__(self, pool, cr):
        init_res = super(IrModel, self).__init__(pool, cr)
        if column_exists(cr, 'ir_model', 'track_user_assignment'):
            cr.execute("""
            SELECT model FROM ir_model WHERE track_user_assignment = True
            """)
            track_user_assignment_whitelisted_models = [row[0] for row in cr.fetchall()]
            tools.config.options['track_user_assignment_whitelisted_models'] = track_user_assignment_whitelisted_models
        return init_res

    track_user_assignment = fields.Boolean(string='Track User Assignment')

    @api.model_create_multi
    @api.returns('self', lambda value:value.id)
    def create(self, vals_list):
        records = super(IrModel, self).create(vals_list)
        self._update_user_assignment_whitelisted_models_config()
        return records

    def write(self, vals):
        res = super(IrModel, self).write(vals)
        if 'track_user_assignment' in vals:
            self._update_user_assignment_whitelisted_models_config()
        return res

    def unlink(self):
        res = super(IrModel, self).unlink()
        self._update_user_assignment_whitelisted_models_config()
        return res

    @api.model
    def _update_user_assignment_whitelisted_models_config(self):
        ir_models = self.search([
            ('track_user_assignment', '=', True)
            ])
        tools.config.options['track_user_assignment_whitelisted_models'] = ir_models.mapped('model')
