from odoo import fields, models


class res_company(models.Model):
    _inherit = 'res.company'

    applicable_on = fields.Selection([('sale', 'Sale Order'), ('purchase', 'Purchase Order'),
          ('sale_purchase', 'Sale and Purchase Order')])
    so_po_auto_validation = fields.Selection([('draft', 'Draft'), ('validated', 'Validated')])

