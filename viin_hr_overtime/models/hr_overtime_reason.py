from odoo import models, fields, api, _

from .res_company import OVERTIME_RECOGNITION_MODE


class HrOvertimeReason(models.Model):
    _name = 'hr.overtime.reason'
    _description = 'Overtime Reason'

    name = fields.Char(string='Title', required=True, translate=True)
    active = fields.Boolean('Active', default=True,
                            help="If the active field is set to false, it will allow you to hide the reason without removing it.")
    description = fields.Text(string='Description')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    recognition_mode = fields.Selection(OVERTIME_RECOGNITION_MODE, string='Recognition Mode', compute='_compute_recognition_mode', store=True, readonly=False)

    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name, company_id)',
         "The reason title must be unique per company."),
    ]

    @api.depends('company_id')
    def _compute_recognition_mode(self):
        for r in self:
            r.recognition_mode = r.company_id.overtime_recognition_mode
