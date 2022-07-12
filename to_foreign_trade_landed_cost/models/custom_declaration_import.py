from odoo import models, fields, api


class CustomDeclarationImport(models.Model):
    _inherit = 'custom.declaration.import'
    
    landed_cost_ids = fields.One2many('stock.landed.cost', 'custom_declaration_import_id', string='Landed Cost')
    landed_cost_count = fields.Integer(string='landed Cost Count', compute='_compute_landed_cost_count', compute_sudo=True)
    
    @api.depends('landed_cost_ids')
    def _compute_landed_cost_count(self):
        for r in self:
            r.landed_cost_count = len(r.landed_cost_ids)
    
    def _prepare_landed_cost_data(self):
        res = super(CustomDeclarationImport, self)._prepare_landed_cost_data()
        res.update({'custom_declaration_import_id': self.id})
        return res
    
    def _should_create_landed_cost(self):
        return True
