from odoo import models, api
from lxml.builder import E


class BaseModel(models.AbstractModel):
    _inherit = 'base'

    @api.model
    def _get_default_dashboard_view(self):
        """ Generates a default viin_dashboard view containing default sub graph and
        pivot views.

        :returns: a viin_dashboard view as an lxml document
        :rtype: etree._Element
        """
        viin_dashboard = E.dashboard()
        viin_dashboard.append(E.view(type="graph"))
        viin_dashboard.append(E.view(type="pivot"))
        return viin_dashboard
