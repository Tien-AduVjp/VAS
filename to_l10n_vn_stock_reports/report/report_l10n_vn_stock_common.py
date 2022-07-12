from odoo import models
from odoo.tools import format_date


class ReportL10n_vnStockCommon(models.AbstractModel):
    _name = 'report.l10n_vn_stock.common'
    _inherit = ['report.l10n_vn.common', 'report.stock.common']
    _description = 'Vietnam C200 Stock Report Common'

    def _formart_datetime_to_date(self, datetime):
        """
        Convert Datetime (UTC) to Date (user tz)
        Format Date by lang
        """
        new_date = self.env['to.base'].convert_utc_time_to_tz(datetime, tz_name=self.env.user.tz).date()
        return format_date(self.env, new_date)
