# -*- coding: utf-8 -*-
from odoo import models, fields


class AccountAnalyticTag(models.Model):
    _inherit = 'account.analytic.tag'

    name = fields.Char(translate=True)
