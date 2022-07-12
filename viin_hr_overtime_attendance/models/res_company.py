from odoo import fields, models, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    overtime_recognition_mode = fields.Selection(selection_add=[('attendance', 'Attendance')])
