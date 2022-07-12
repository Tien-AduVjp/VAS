from odoo import fields, models


class res_company(models.Model):
    _inherit = 'res.company'

    unique_doc_name = fields.Boolean(string='Unique Document Name',
                                     help="Default value for new workspaces for document name unique violation checking")
