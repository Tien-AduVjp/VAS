from odoo import models, fields, api, _
from odoo.tools import float_compare
from odoo.exceptions import ValidationError


class ResCompany(models.Model):
    _inherit = 'res.company'

    vendor_app_comm_percent = fields.Float(string="Default Apps Commission Percentage", default=30.0,
                                    help="When selling our vendors' Odoo Modules, we take this as our commission")
    vendor_app_min_payout = fields.Monetary(string='Min. Payout', default=400.0,
                                            help="We do not pay the vendor if total purchase amount is less than this")
    dedicated_app_download_token_lifetime = fields.Boolean(string='Use Dedicated Apps Download Token Lifetime',
                                                           default=True,
                                                           help="If enabled, download token lifetime will be applied"
                                                           " by the Download Token Lifetime specified below. Otherwise,"
                                                           " the global Default Token Lifetime will be used.")
    app_download_token_lifetime = fields.Float(string='Download Token Lifetime', default=3.0,
                                               help="The lifetime (in days) of app download tokens. Leave it zero"
                                               " for permanent tokens")

    @api.constrains('app_download_token_lifetime')
    def _check_app_download_token_lifetime(self):
        for r in self:
            if float_compare(r.app_download_token_lifetime, 0.0, precision_digits=2) == -1:
                raise ValidationError(_("Download Token Lifetime must be greater than or equal to zero"))

