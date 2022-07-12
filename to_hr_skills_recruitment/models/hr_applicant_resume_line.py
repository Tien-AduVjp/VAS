from odoo import fields, models


class ResumeLine(models.Model):
    _name = 'hr.applicant.resume.line'
    _description = 'Resumé line of an applicant'
    _order = 'line_type_id, date_end desc, date_start desc'

    hr_applicant_id = fields.Many2one('hr.applicant', required=True, ondelete='cascade', string='Applicant')
    name = fields.Char(required=True, string='Name')
    date_start = fields.Date(required=True, string='Date Start')
    date_end = fields.Date(string='Date End')
    description = fields.Text(string='Description')
    line_type_id = fields.Many2one('hr.resume.line.type', string='Type')

    # Used to apply specific template on a line
    display_type = fields.Selection([('classic', 'Classic')], string='Display Type', default='classic')

    _sql_constraints = [
        ('date_check', 'CHECK (date_start <= date_end)', "The start date must be anterior to the end date."),
    ]
