from odoo import fields, models


class Employee(models.Model):
    _inherit = 'hr.employee'

    name = fields.Char(tracking=True)
    address_id = fields.Many2one(tracking=True)
    address_home_id = fields.Many2one(tracking=True)
    work_email = fields.Char(tracking=True)
    job_id = fields.Many2one(tracking=True)
    department_id = fields.Many2one(tracking=True)
    work_phone = fields.Char(tracking=True)
    mobile_phone = fields.Char(tracking=True)
    parent_id = fields.Many2one(tracking=True)
    coach_id = fields.Many2one(tracking=True)
    work_location = fields.Char(tracking=True)
