from odoo import models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _register_hook(self):
        super(SaleOrderLine, self)._register_hook()
        prepare_invoice_line_origin = self.__class__._prepare_invoice_line

        def _prepare_invoice_line_with_vietsub(sol):
            res = prepare_invoice_line_origin(sol)
            if sol._context.get('add_invoice_line_name_vietsub', True):
                journal = sol.env['account.move'].with_context(default_type='out_invoice')._get_default_journal()
                if sol.product_id and sol.order_id.partner_id.country_id != sol.env.ref('base.vn') and \
                        sol.order_id.partner_id.lang != 'vi_VN' and journal.einvoice_enabled:
                    new_invoice_line_name = sol._get_invoice_line_name_vietsub()
                    new_invoice_line_name += ' (%s)' % res['name']
                    res.update({'name': new_invoice_line_name})
            return res

        self.__class__._prepare_invoice_line = _prepare_invoice_line_with_vietsub

    def _get_invoice_line_name_vietsub(self):
        self = self.with_context(lang='vi_VN')
        return self.product_id.description_sale or self.product_id.name
