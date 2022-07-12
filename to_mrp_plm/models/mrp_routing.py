from odoo import api, fields, models


class MrpRouting(models.Model):
    _inherit = 'mrp.routing'

    version = fields.Integer(string='Version', default=0)
    previous_routing_id = fields.Many2one('mrp.routing', string='Previous Routing')
    revision_ids = fields.Many2many('mrp.routing', compute='_compute_revision_ids')
    eco_ids = fields.One2many('mrp.eco', 'new_routing_id', string='ECOs')
    eco_count = fields.Integer(string='# ECOs', compute='_compute_eco_count')

    def _compute_revision_ids(self):
        for r in self:
            pre_routings = self.env['mrp.routing']
            this = r
            while this.previous_routing_id:
                pre_routings |= this
                this = this.previous_routing_id
            r.revision_ids = pre_routings.ids

    def _compute_eco_count(self):
        ecos = self.env['mrp.eco'].read_group([('new_routing_id', 'in', self.ids)], ['new_routing_id'], ['new_routing_id'])
        mapped_data = dict([(d['new_routing_id'][0], d['new_routing_id_count']) for d in ecos])
        for r in self:
            r.eco_count = mapped_data.get(r.id, 0)

    def _action_apply_new_version(self):
        self.write({'active': True})
        self.previous_routing_id.write({'active': False})
