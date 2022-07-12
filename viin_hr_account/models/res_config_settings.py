from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    general_employee_payable_account_id = fields.Many2one(
        related='company_id.general_employee_payable_account_id',
        readonly=False, groups="account.group_account_user",
        domain="[('deprecated','=',False),('company_id','=',current_company_id)]"
        )
