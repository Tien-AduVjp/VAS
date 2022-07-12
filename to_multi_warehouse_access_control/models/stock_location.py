from odoo import models, fields, api


class StockLocation(models.Model):
    _inherit = 'stock.location'

    access_user_ids = fields.Many2many('res.users', string='Accessing Users', compute='_compute_access_user_ids', store=True,
                                help="The users who have access to this location and do all stock operations concern this location")

    @api.depends('warehouse_id', 'warehouse_id.access_user_ids')
    def _compute_access_user_ids(self):
        for r in self:
            if r.warehouse_id and r.warehouse_id.access_user_ids:
                r.access_user_ids = r.warehouse_id.access_user_ids.ids
            else:
                r.access_user_ids = False
