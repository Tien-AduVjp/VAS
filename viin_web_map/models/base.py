from odoo import api, models
from lxml.builder import E

class Base(models.AbstractModel):
    _inherit = 'base'

    @api.model
    def _get_default_map_view(self):
        view = E.map()
        return view
