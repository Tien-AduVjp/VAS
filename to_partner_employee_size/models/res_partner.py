from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    employee_size_id = fields.Many2one('res.partner.employee.size', string="Employee Size", ondelete='restrict', tracking=True)
    
    @api.onchange('company_type')
    def onchange_company_type(self):
        super(ResPartner, self).onchange_company_type()
        if self.company_type == 'person':
            self.employee_size_id = False
        elif self.company_type == 'company' and self._origin:
            self.employee_size_id = self._origin.employee_size_id
        