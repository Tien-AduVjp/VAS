from odoo import models, fields, api


class CustomDeclarationExport(models.Model):
    _inherit = 'custom.declaration.export'

    landed_cost_ids = fields.One2many('stock.landed.cost', 'custom_declaration_export_id', string='Landed Cost')
    landed_cost_count = fields.Integer(string='landed Cost Count', compute='_compute_landed_cost_count', compute_sudo=True)
    
    @api.depends('landed_cost_ids')
    def _compute_landed_cost_count(self):
        for r in self:
            r.landed_cost_count = len(r.landed_cost_ids)
    
    def _prepare_landed_cost_data(self):
        res = super(CustomDeclarationExport, self)._prepare_landed_cost_data()
        res.update({'custom_declaration_export_id': self.id})
        return res
