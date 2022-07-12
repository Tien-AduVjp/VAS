from odoo import api, models


class ZoomUserReport(models.AbstractModel):
    _name = 'report.to_zoom_calendar.report_zoom_user'
    _description = 'Zoom User Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        return {
            'data': data,
        }
