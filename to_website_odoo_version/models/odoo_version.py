# -*- coding: utf-8 -*-

from odoo import models


class OdooVersion(models.Model):
    _name = 'odoo.version'
    _inherit = ['odoo.version', 'website.published.mixin']

