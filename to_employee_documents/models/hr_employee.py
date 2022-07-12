from odoo import fields, models, api


class Employee(models.Model):
    _inherit = 'hr.employee'

    document_ids = fields.One2many('employee.document', 'employee_id', string='HR Documents')
    document_count = fields.Integer(string="Employee Document Count", compute='_compute_document_count')

    def _compute_document_count(self):
        docs_data = self.env['employee.document'].read_group([('employee_id', 'in', self.ids)], ['employee_id'], ['employee_id'])
        mapped_data = dict([(dict_data['employee_id'][0], dict_data['employee_id_count']) for dict_data in docs_data])
        for r in self:
            r.document_count = mapped_data.get(r.id, 0)
