# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    noindex_nofollow = fields.Boolean(related='website_id.noindex_nofollow', readonly=False)