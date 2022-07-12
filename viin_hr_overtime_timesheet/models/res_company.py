from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    overtime_recognition_mode = fields.Selection(selection_add=[('timesheet', 'Timesheet')])
