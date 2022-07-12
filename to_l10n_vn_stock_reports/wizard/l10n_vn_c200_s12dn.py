from odoo import fields, models, api


class WizardL10n_vnC200_s12dn(models.TransientModel):
    _name = 'wizard.l10n_vn.c200_s12dn'
    _inherit = 'wizard.stock.report.common'
    _description = 'Vietnam C200 S12-DN Report Wizard'

    product_id = fields.Many2one('product.product', string="Product", domain=[('type', '!=', 'service')], required=True)
    description = fields.Text(string="Product Description", related='product_id.description_picking', readonly=True)
    uom_id = fields.Many2one('uom.uom', related='product_id.uom_id', readonly=True)
    default_code = fields.Char(string="Internal Reference", related='product_id.default_code', readonly=True)
    opening_date = fields.Date(string="Opening Date", compute='_compute_opening_date')

    @api.depends('product_id', 'location_id')
    def _compute_opening_date(self):
        for r in self:
            stock_move = self.env['stock.move'].search([
                ('product_id', '=', r.product_id.id),
                ('location_dest_id', 'in', r.location_id.get_sublocations().ids)
                ], order='date', limit=1)

            r.opening_date = stock_move and stock_move.date.date() or fields.Date.today()

    def _print_report(self, data):
        data['form'].update(self.read(['warehouse_id', 'location_id', 'product_id', 'description', 'uom_id', 'default_code', 'opening_date'])[0])
        res = self.env.ref('to_l10n_vn_stock_reports.act_report_c200_s12dn').report_action(self, data=data)
        return res
