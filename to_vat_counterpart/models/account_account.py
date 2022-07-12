import logging
from odoo import models

_logger = logging.getLogger(__name__)

class AccountAcount(models.Model):
    _inherit = 'account.account'

    def _get_vat_counterpart_account(self, company):
        # TODO: remove me in master/15+
        _logger.warning("The method _get_vat_counterpart_account() of the account.account"
                        " is deprecated and will be remove soon. Please use the res.company's"
                        " property_vat_ctp_account_id field instead.")
        return company.property_vat_ctp_account_id
