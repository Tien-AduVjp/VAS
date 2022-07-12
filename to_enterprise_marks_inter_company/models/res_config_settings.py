# -*- coding: utf-8 -*-
from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_to_inter_company_base = fields.Boolean("Setup Inter-Company Base")

