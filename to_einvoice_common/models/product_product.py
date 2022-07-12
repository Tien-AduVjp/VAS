from odoo import models, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.depends_context('partner_id', 'display_default_code')
    def _compute_partner_ref(self):
        super(ProductProduct, self)._compute_partner_ref()

    def with_context(self, *args, **kwargs):
        # override to handle issue of _get_computed_name method in account move line
        # https://github.com/Viindoo/odoo/blob/d3c6e88790ea3031d4a4cc89c32a68c00f12014e/addons/account/models/account_move.py#L2825
        # it gets name based on lang of partner while we want to get vietnamese name,
        # so we have to add a context to patch it
        if kwargs.get('einvoice_line_name_vi_VN') or self._context.get('einvoice_line_name_vi_VN'):
            kwargs.update({
                'lang': 'vi_VN'
            })
        return super(ProductProduct, self).with_context(*args, **kwargs)
