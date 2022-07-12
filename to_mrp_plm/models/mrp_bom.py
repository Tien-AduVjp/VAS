import ast

from odoo import api, fields, models


class MrpBom(models.Model):
    _inherit = 'mrp.bom'
    
    version = fields.Integer(string='Version', default=0)
    previous_bom_id = fields.Many2one('mrp.bom', string='Previous BoM')
    active = fields.Boolean(string='Active')
    image_128 = fields.Binary(related='product_tmpl_id.image_128')
    eco_ids = fields.One2many('mrp.eco', 'new_bom_id', string='ECO to be applied')
    eco_count = fields.Integer(string='# ECOs', compute='_compute_eco_data')
    eco_inprogress_count = fields.Integer(string="# ECOs in progress", compute='_compute_eco_data')
    revision_ids = fields.Many2many('mrp.bom', compute='_compute_revisions')

    def _compute_eco_data(self):
        ecos = self.env['mrp.eco'].search([('new_bom_id', 'in', self.ids)])
        ecos.read(['state'])
        for r in self:
            all_ecos = ecos.filtered(lambda eco: eco.new_bom_id == r)
            eco_progress = all_ecos.filtered(lambda eco: eco.state == 'progress')
            r.eco_count = len(all_ecos)
            r.eco_inprogress_count = len(eco_progress)

    def _compute_revisions(self):
        for r in self:
            pre_boms = self.env['mrp.bom']
            this = r
            while this.previous_bom_id:
                pre_boms |= this
                this = this.previous_bom_id
            r.revision_ids = pre_boms.ids

    def _action_apply_new_version(self):
        self.write({'active': True})
        self.previous_bom_id.write({'active': False})

    def button_mrp_eco(self):
        self.ensure_one()
        action = self.env.ref('to_mrp_plm.mrp_eco_action_main').read()[0]
        
        ctx = action.get('context', {})
        if type(ctx) == str:
            ctx = ast.literal_eval(ctx)        
        ctx.update({'default_bom_id': self.id,
                    'default_product_tmpl_id': self.product_tmpl_id.id,
                    })
        
        action['context'] = ctx
        action['domain'] = [('id', 'in', self.eco_ids.ids)]
        return action
