from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    odoo_module_id = fields.Many2one('odoo.module', string='Odoo Module')
    odoo_module_version_id = fields.Many2one('odoo.module.version', string='Odoo Module Version')

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        fields.update({
            'odoo_module_id': ", om.id AS odoo_module_id",
            'odoo_module_version_id': ", omv.id AS odoo_module_version_id"
        })

        from_clause = """
        %s
        LEFT JOIN odoo_module_version AS omv ON omv.id = p.odoo_module_version_id
        LEFT JOIN odoo_module AS om ON om.id = omv.module_id
        """ % from_clause

        groupby = """
        %s,
        om.id,
        omv.id
        """ % groupby
        return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)
