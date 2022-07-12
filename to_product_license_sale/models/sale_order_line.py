from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_license_version_ids = fields.Many2many('product.license.version', 'sale_line_product_license_version_rel', 'sale_line_id', 'product_license_version_id',
                                                   compute='_compute_product_license_version_ids', store=True,
                                                   string='Licenses', help="The license version(s) that you want to license for the product sold.")

    def _get_license_text(self):
        if self.order_id.partner_id.lang:
            self = self.with_context(lang=self.order_id.partner_id.lang)
        if self.product_id.product_license_version_ids:
            return '\n' + _("License: ") + ', '.join(self.product_id.product_license_version_ids.mapped('display_name'))
        else:
            return ''

    def _set_license_text_to_name(self):
        for r in self:
            license_info = r._get_license_text()
            if r.product_id and r.name and license_info not in r.name:
                r.name += license_info

    @api.depends('product_id')
    def _compute_product_license_version_ids(self):
        for r in self:
            r.product_license_version_ids = [(6, 0, r.product_id.product_license_version_ids.ids)]
            r._set_license_text_to_name()

    def _refresh_for_licenses(self):
        """
        This tool allows users to update the sales order lines with the latest licenses configured by the corresponding products.
        """
        for r in self:
            if r.state not in ('draft', 'sent'):
                raise UserError(_("You could not refresh the sales order line '%s' of the sales order '%s'"
                                  " while its state is neither 'Quotation' nor 'Quotation Sent'")
                                  % (r.display_name, r.order_id.name))
            r.name = r.get_sale_order_line_multiline_description_sale(r.product_id)
        self._compute_product_license_version_ids()
