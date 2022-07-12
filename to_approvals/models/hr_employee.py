from odoo import models, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    @api.model_create_multi
    @api.returns('self', lambda value:value.id)
    def create(self, vals_list):
        employees = super(HrEmployee, self).create(vals_list)
        self.env['ir.rule'].clear_caches()
        return employees
    
    def write(self, vals):
        res = super(HrEmployee, self).write(vals)
        self.env['ir.rule'].clear_caches()
        return res
    
    def unlink(self):
        res = super(HrEmployee, self).unlink()
        self.env['ir.rule'].clear_caches()
        return res
