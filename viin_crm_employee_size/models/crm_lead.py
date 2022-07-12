from odoo import fields, models


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    employee_size_id = fields.Many2one('res.partner.employee.size', string='Employee Size')
