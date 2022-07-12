from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    applicable_on = fields.Selection([('sale', 'Sale Order'), ('purchase', 'Purchase Order'),
        ('sale_purchase', 'Sale and Purchase Order')], related='rules_company_id.applicable_on', readonly=False)
    so_po_auto_validation = fields.Selection([('draft', 'draft'), ('validated', 'validated')],
                                       related='rules_company_id.so_po_auto_validation', readonly=False)
    rules_company_id = fields.Many2one('res.company', string='Select Company',
        help='Select company to setup Inter company rules.', default=lambda self: self.env.company, readonly=True)

