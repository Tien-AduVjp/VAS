from odoo import models, fields


class HrDepartment(models.Model):
    _inherit = 'hr.department'

    rank_ids = fields.One2many('hr.rank', 'department_id', string='Ranks', help="The ranks that are dedicated for this department.")
    ranks_count = fields.Integer(string='Ranks Count', compute='_compute_ranks_count')

    def _compute_ranks_count(self):
        ranks_data = self.env['hr.rank'].read_group([('department_id', 'in', self.ids)], ['department_id'], ['department_id'])
        mapped_data = dict([(dict_data['department_id'][0], dict_data['department_id_count']) for dict_data in ranks_data])
        for r in self:
            r.ranks_count = mapped_data.get(r.id, 0)

    def action_view_ranks(self):
        action = self.env['ir.actions.act_window']._for_xml_id('viin_hr_rank.action_hr_rank')
        action['context'] = {
            'default_department_id': self[:1].id,
            }
        action['domain'] = "[('department_id','in',%s)]" % self.ids
        return action
