from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    inter_comp_warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse For Purchase Orders',
                                              related='rules_company_id.inter_comp_warehouse_id', readonly=False,
                                              domain="[('company_id', '=', company_id)]",
                                              help="Default value to set on Purchase Orders that will be created based on Sales Orders made"
                                              " to this company.")

