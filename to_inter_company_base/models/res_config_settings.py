from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_to_inter_company_sale_purchase = fields.Boolean("Inter-Company for Sale/Purchase")
    module_to_inter_company_invoice = fields.Boolean("Inter-Company for Invoices")
    intercompany_user_id = fields.Many2one(related='company_id.intercompany_user_id', readonly=False)

    @api.constrains('module_to_inter_company_sale_purchase', 'module_to_inter_company_sale_purchase')
    def _check_require_module_to_inter_company_invoice(self):
        for r in self:
            if r.module_to_inter_company_sale_purchase and not r.module_to_inter_company_invoice:
                raise UserError(_("Inter-Company for Invoices must be enabled while Inter-Company for Sale/Purchase is enabled."))

    @api.onchange('module_to_inter_company_sale_purchase')
    def _onchange_module_to_inter_company_sale_purchase(self):
        if self.module_to_inter_company_sale_purchase:
            self.module_to_inter_company_invoice = True

    @api.onchange('module_to_inter_company_invoice')
    def _onchange_module_to_inter_company_invoice(self):
        if not self.module_to_inter_company_invoice:
            self.module_to_inter_company_sale_purchase = False
