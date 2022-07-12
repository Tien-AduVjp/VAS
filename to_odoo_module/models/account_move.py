from odoo import models, fields, api
from odoo.tools import float_is_zero


class AccountMove(models.Model):
    _inherit = 'account.move'

    reversed_entry_ids = fields.One2many('account.move', 'reversed_entry_id', string='Reversed Entries', readonly=True)
    odoo_module_version_ids = fields.Many2many('odoo.module.version', string='Odoo Module Versions', compute='_compute_odoo_module_versions')
    odoo_module_versions_count = fields.Integer(string='Odoo Module Versions Count', compute='_compute_odoo_module_versions')
    auto_load_app_dependencies = fields.Boolean(string='Auto Load Apps Dependencies', default=True, help="If checked, upon on changing of invoice lines,"
                                                " Odoo will check if any Odoo Module Dependency is needed to load. The dependecies that already bought"
                                                " before will not be loaded.")

    def _compute_odoo_module_versions(self):
        prec = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for r in self.sudo():
            odoo_module_versions = r.invoice_line_ids.get_odoo_module_versions(prec)
            r.update({
                'odoo_module_version_ids': odoo_module_versions.ids,
                'odoo_module_versions_count': len(odoo_module_versions)
                })

    def action_view_odoo_module_versions(self):
        odoo_module_versions = self.mapped('odoo_module_version_ids')
        result = self.env["ir.actions.act_window"]._for_xml_id('to_odoo_module.odoo_module_version_action')

        # get rid off the default context
        result['context'] = {}
        # choose the view_mode accordingly
        modules_count = len(odoo_module_versions)
        if modules_count != 1:
            result['domain'] = "[('id', 'in', %s)]" % str(odoo_module_versions.ids)
        elif modules_count == 1:
            res = self.env.ref('to_odoo_module.odoo_module_version_form_view', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = odoo_module_versions.id
        return result

    def _update_odoo_module_dependency_lines(self):
        uom_precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        invoice_line_ids = self.invoice_line_ids

        # product already added in the invoice
        products_existing_in_invoice = self.invoice_line_ids.filtered(lambda l: not float_is_zero(l.quantity, precision_digits=uom_precision)).sudo().product_id

        # app product dependencies
        app_product_dependencies = products_existing_in_invoice.with_context(partner=self.partner_id).get_app_product_dependencies()

        # find the missing
        missing = app_product_dependencies - products_existing_in_invoice

        if missing:
            sequence = 10
            for product in missing:
                sequence += 1
                invl_vals = {'move_id': self.id}
                invl_vals.update(product._prepare_app_dependency_line_data(sequence=sequence))
                new_line = invoice_line_ids.new(invl_vals)
                new_line._onchange_product_id()
                new_line._onchange_price_subtotal()
                invoice_line_ids += new_line
            self.with_context(no_update_module_dependencies=True).invoice_line_ids = invoice_line_ids

    @api.onchange('invoice_line_ids')
    def _onchange_invoice_line_ids(self):
        if self.invoice_line_ids and self.mapped('odoo_module_version_ids') and self.auto_load_app_dependencies:
            self._update_odoo_module_dependency_lines()
        super(AccountMove, self)._onchange_invoice_line_ids()
