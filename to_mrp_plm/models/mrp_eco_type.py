import ast

from odoo import fields, models


class MrpEcoType(models.Model):
    _name = "mrp.eco.type"
    _description = 'Manufacturing Process'
    _inherit = ['mail.alias.mixin', 'mail.thread']

    name = fields.Char(string='Type Name', required=True, translate=True)
    sequence = fields.Integer(string='Sequence')
    alias_id = fields.Many2one('mail.alias', string='Alias', ondelete='restrict', required=True)

    nb_ecos = fields.Integer(string='ECOs', compute='_compute_nb')
    nb_approvals = fields.Integer(string='Waiting Approvals', compute='_compute_nb')
    nb_approvals_my = fields.Integer(string='Waiting my Approvals', compute='_compute_nb')
    nb_validation = fields.Integer(string='To Apply', compute='_compute_nb')
    color = fields.Integer(string='Color')
    stage_ids = fields.Many2many('mrp.eco.stage', string='Stages')


    def _compute_nb(self):
        for r in self:
            ecos = self.env['mrp.eco'].search([('type_id', '=', r.id)])
            r.nb_ecos = len(ecos)
            r.nb_approvals = len(ecos.filtered(lambda e: 'none' in e.approval_ids
                                                                    .filtered(lambda ap: ap.template_stage_id == e.stage_id)
                                                                    .mapped('status')))
            r.nb_approvals_my = len(ecos.filtered(lambda e: e.need_my_approval))
            r.nb_validation = len(ecos.filtered(lambda e: e.allow_apply_change))

    def _alias_get_creation_values(self):
        values = super(MrpEcoType, self)._alias_get_creation_values()
        values['alias_model_id'] = self.env['ir.model']._get('mrp.eco').id
        if self.id:
            values['alias_defaults'] = defaults = ast.literal_eval(self.alias_defaults or "{}")
            defaults['type_id'] = self.id
        return values
