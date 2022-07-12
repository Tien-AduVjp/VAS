from odoo import models


class ReportAccountCoa(models.AbstractModel):
    _inherit = 'account.coa.report'

    filter_show_ignored_entries = None
