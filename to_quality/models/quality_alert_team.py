from odoo import api, fields, models


class QualityAlertTeam(models.Model):
    _name = "quality.alert.team"
    _description = "Quality Alert Team"
    _inherit = ['mail.alias.mixin', 'mail.thread']
    _order = "sequence, id"

    name = fields.Char(string='Name', required=True, translate=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    sequence = fields.Integer(string='Sequence')
    color = fields.Integer(string='Color', default=1)
    alias_id = fields.Many2one('mail.alias',  string='Alias', ondelete="restrict", required=True)
    check_count = fields.Integer(string='# Quality Checks', compute='_compute_check_count')
    alert_count = fields.Integer(string='# Quality Alerts', compute='_compute_alert_count')

    def _prepare_count_values(self, model, domain, fields,  groupby):
        data = self.env[model].read_group(domain, fields, groupby)
        dict = {}
        for d in data:
            dict[d['team_id'][0]] = d['team_id_count']
        return dict

    def _compute_check_count(self):
        dict_count = self._prepare_count_values('quality.check', [('team_id', 'in', self.ids), ('quality_state', '=', 'none')],
                                                ['team_id'],  ['team_id'])
        for r in self:
            if r.id in dict_count.keys():
                r.check_count = dict_count[r.id]
            else:
                r.check_count = 0

    def _compute_alert_count(self):
        dict_count = self._prepare_count_values('quality.alert', [('team_id', 'in', self.ids), ('stage_id.done', '=', False)],
                                                ['team_id'],  ['team_id'])
        for r in self:
            if r.id in dict_count.keys():
                r.alert_count = dict_count[r.id]
            else:
                r.alert_count = 0

    def get_alias_model_name(self, vals):
        return vals.get('alias_model', 'quality.alert')

    def get_alias_values(self):
        values = super(QualityAlertTeam, self).get_alias_values()
        values['alias_defaults'] = {'team_id': self.id}
        return values
