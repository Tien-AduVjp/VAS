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
    alias_name = fields.Char(help="The name of the email alias, e.g. 'jobs' if you want to catch emails for <jobs@example.viindoo.com>")

    def _compute_nb(self):
        MrpEco = self.env['mrp.eco']
        for r in self:
            r.nb_ecos = MrpEco.search_count([('type_id', '=', r.id),('state', '!=', 'done')])
            r.nb_approvals = MrpEco.search_count([
                ('type_id', '=', r.id), 
                ('approval_ids.status', '=', 'none')])
            r.nb_approvals_my = MrpEco.search_count([
                ('type_id', '=', r.id), 
                ('approval_ids.status', '=', 'none'),
                ('approval_ids.required_user_ids', '=', self.env.user.id)])
            r.nb_validation = MrpEco.search_count([
                ('type_id', '=', r.id), 
                ('stage_id.is_final_stage', '=', True), 
                ('state', '=', 'progress')])

    def get_alias_model_name(self, vals):
        return vals.get('alias_model', 'mrp.eco')

    def get_alias_values(self):
        res = super(MrpEcoType, self).get_alias_values()
        res['alias_defaults'] = {'type_id': self.id}
        return res
