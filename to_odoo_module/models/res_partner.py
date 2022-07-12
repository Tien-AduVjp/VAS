from odoo import models, fields
from odoo.osv import expression


class ResPartner(models.Model):
    _inherit = 'res.partner'

    paid_odoo_module_version_ids = fields.Many2many('odoo.module.version', string='Paid Odoo Module Versions', compute='_compute_paid_odoo_apps')
    paid_odoo_module_versions_count = fields.Integer(string='Sold Apps Count', compute='_compute_paid_odoo_apps')
    paid_odoo_app_product_ids = fields.Many2many('product.product', string='Paid Odoo App Products', compute='_compute_paid_odoo_apps')

    def _get_paid_odoo_app_inv_line_domain(self, use_commercial_partner=True):
        """
        This method provides domain for searching paid invoice lines related to the partner in self        
        """
        domain = [
            ('move_id.invoice_payment_state', '=', 'paid'),
            ('move_id.type', '=', 'out_invoice'),
            '|', ('move_id.reversed_entry_ids', '=', False), ('move_id.reversed_entry_ids.state', '!=', 'posted')]
        if use_commercial_partner:
            partner_domain = [('move_id.partner_id.commercial_partner_id', '=', self.commercial_partner_id.id)]
        else:
            partner_domain = [
                '|',
                    '&', ('move_id.partner_id.is_company', '=', False), ('move_id.partner_id', '=', self.id),
                    '&', ('move_id.partner_id.is_company', '=', True), ('move_id.partner_id.commercial_partner_id', '=', self.commercial_partner_id.id)
                    ]
        domain = expression.AND([partner_domain, domain])
        return domain

    def get_paid_odoo_apps(self, use_commercial_partner=True):
        """
        @param use_commercial_partner: all partners that belong to the commercial partner of the invoice can obtain paid apps
        @type use_commercial_partner: bool

        @return: tuple of paid odoo module versions and paid odoo app products
        @rtype: tuple
        """
        self.ensure_one()
        paid_invoice_lines = self.env['account.move.line'].sudo().search(self._get_paid_odoo_app_inv_line_domain(use_commercial_partner=use_commercial_partner))
        paid_odoo_module_versions = paid_invoice_lines.odoo_module_version_id
        paid_odoo_app_products = paid_invoice_lines.product_id
        return paid_odoo_module_versions, paid_odoo_app_products

    def _compute_paid_odoo_apps(self):
        for r in self:
            paid_odoo_module_versions, paid_odoo_app_products = r.get_paid_odoo_apps(use_commercial_partner=True)
            r.update({
                'paid_odoo_module_version_ids': [(6, 0, paid_odoo_module_versions.ids)],
                'paid_odoo_app_product_ids': [(6, 0, paid_odoo_app_products.ids)],
                'paid_odoo_module_versions_count': len(paid_odoo_module_versions)
                })

    def action_view_sold_odoo_apps(self):
        self.ensure_one()
        action = self.env.ref('to_odoo_module.odoo_module_version_action')
        result = action.read()[0]

        # reset context
        result['context'] = {}
        paid_odoo_module_versions = self.paid_odoo_module_version_ids
        result['domain'] = "[('id', 'in', %s)]" % str(paid_odoo_module_versions.ids)
        return result

