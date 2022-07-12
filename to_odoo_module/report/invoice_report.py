from odoo import fields, models


class AccountInvoiceReport(models.Model):
    _inherit = 'account.invoice.report'

    odoo_module_id = fields.Many2one('odoo.module', string='Odoo Module')
    odoo_module_version_id = fields.Many2one('odoo.module.version', string='Odoo Module Version')

    def _select(self):
        return super(AccountInvoiceReport, self)._select() + ", omv.id as odoo_module_version_id, om.id as odoo_module_id"

    def _from(self):
        from_str = super(AccountInvoiceReport, self)._from()
        from_str += """
        LEFT JOIN odoo_module_version AS omv ON omv.id = product.odoo_module_version_id
        LEFT JOIN odoo_module AS om ON om.id = omv.module_id
        """
        return from_str
