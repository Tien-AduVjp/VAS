from odoo import models, fields, api
from odoo.tools import float_is_zero


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    odoo_module_version_ids = fields.Many2many('odoo.module.version', string='Odoo Module Versions', compute='_compute_odoo_module_versions')
    odoo_module_versions_count = fields.Integer(string='Odoo Module Versions Count', compute='_compute_odoo_module_versions')
    auto_load_app_dependencies = fields.Boolean(string='Auto Load Apps Dependencies', default=True, help="If checked, upon on changing of order lines,"
                                                " Odoo will check if any Odoo Module Dependency is needed to load. The dependecies that already bought"
                                                " before will not be loaded.")
    exclude_already_purchased_apps = fields.Boolean(string='Exclude Already-Purchased Apps', default=True,
                                                    help="If checked, the Autoload Apps Dependencies will exclude the apps that the customer has purchased and paid.")
    print_app_desc_on_sale_order = fields.Boolean(string='Print App Description', default=True,
                                                help="If enabled, PDF version of this will include the description of the related Odoo Apps.\n"
                                                "Note: if the option 'App Description on PDF Quotation/Sale Order' is unchecked on the Product form,"
                                                " the App description will not be included anyway.")

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.partner_id:
            self.exclude_already_purchased_apps = self.partner_id.commercial_partner_id.exclude_already_purchased_apps
        return super(SaleOrder, self).onchange_partner_id()

    def _compute_odoo_module_versions(self):
        prec = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for r in self:
            odoo_module_version_ids = r.order_line.get_odoo_module_versions(prec)
            r.update({
                'odoo_module_version_ids': odoo_module_version_ids.ids,
                'odoo_module_versions_count': len(odoo_module_version_ids)
                })

    def _update_odoo_module_dependency_lines(self):
        """
        This method will find all the not-yet-bought dependencies of the current selected products and update those to the quotation
        """
        uom_precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        line_ids = self.order_line

        # already added in the sale order
        product_existed_in_order = self.order_line.filtered(lambda l: not float_is_zero(l.product_uom_qty, precision_digits=uom_precision)).sudo().product_id

        # find the missing
        if self.exclude_already_purchased_apps:
            dependencies_app_products = product_existed_in_order.with_context(
                    partner=self.partner_id
                ).get_app_product_dependencies()
        else:
            dependencies_app_products = product_existed_in_order.with_context(exclude_paid_apps=False).get_app_product_dependencies()
        missing = dependencies_app_products - product_existed_in_order

        # find the biggest sequence in the existing lines
        last_sequence = line_ids._get_biggest_sequence()
        if missing:
            for product_id in missing:
                last_sequence += 1
                ol_vals = {'order_id': self.id}
                ol_vals.update(product_id._prepare_app_dependency_line_data(quantity_field_name='product_uom_qty', sequence=last_sequence))
                new_line = line_ids.new(ol_vals)
                new_line.product_id_change()
                line_ids += new_line

            self.with_context(no_update_module_dependencies=True).order_line = line_ids

    @api.onchange('order_line')
    def _onchange_order_line_for_apps(self):
        if self.order_line and self.mapped('odoo_module_version_ids') and self.auto_load_app_dependencies:
            self._update_odoo_module_dependency_lines()

    def action_view_odoo_module_versions(self):
        odoo_module_version_ids = self.mapped('odoo_module_version_ids')
        action = self.env.ref('to_odoo_module.odoo_module_version_action')
        result = action.read()[0]

        # get rid off the default context
        result['context'] = {}

        # choose the view_mode accordingly
        modules_count = len(odoo_module_version_ids)
        if modules_count != 1:
            result['domain'] = "[('id', 'in', " + str(odoo_module_version_ids.ids) + ")]"
        elif modules_count == 1:
            res = self.env.ref('to_odoo_module.odoo_module_version_form_view', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = odoo_module_version_ids.id
        return result
