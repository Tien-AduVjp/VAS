from odoo import fields, models


class Contract(models.Model):
    _inherit = 'hr.contract'

    department_id = fields.Many2one(tracking=True)
    job_id = fields.Many2one(tracking=True)
    resource_calendar_id = fields.Many2one(tracking=True)
    wage = fields.Monetary(tracking=True)
    struct_id = fields.Many2one(tracking=True)


class Employee(models.Model):
    _inherit = "hr.employee"

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
