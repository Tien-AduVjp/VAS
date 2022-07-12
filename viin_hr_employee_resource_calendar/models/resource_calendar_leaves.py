# -*- coding: utf-8 -*-

from odoo import models, fields


class ResourceCalendarLeaves(models.Model):
    _inherit = "resource.calendar.leaves"

    holiday = fields.Boolean(string='Holiday', help="If enabled, this leave will be considered as holiday")
