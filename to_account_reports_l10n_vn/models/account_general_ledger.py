from odoo import models
from odoo.osv import expression


class ReportAccountGeneralLedger(models.AbstractModel):
    _inherit = "account.general.ledger"

    def _get_unaffected_earnings_domain(self):
        domain = super(ReportAccountGeneralLedger, self)._get_unaffected_earnings_domain()
        domain = expression.AND([domain, [('account_id.user_type_id', '!=', self.env.ref('account.data_account_type_depreciation').id)]])
        return domain
