from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    payslip_batch_journal_entry = fields.Boolean(related='company_id.payslip_batch_journal_entry', readonly=False)
