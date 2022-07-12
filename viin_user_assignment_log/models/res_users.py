from odoo import models, fields


class ResUsers(models.Model):
    _inherit = 'res.users'

    user_assignment_ids = fields.One2many('user.assignment', 'user_id', string='Assignments', readonly=True)
    user_assignments_count = fields.Integer(string='Assignments Count', compute='_compute_user_assignments_count')

    def __init__(self, pool, cr):
        """ Override of __init__ to add access rights.
            Access rights are disabled by default, but allowed
            on some specific fields defined in self.SELF_{READ/WRITE}ABLE_FIELDS.
        """
        user_assignment_readable_fields = [
            'user_assignment_ids',
            'user_assignments_count',
        ]
        init_res = super(ResUsers, self).__init__(pool, cr)
        type(self).SELF_READABLE_FIELDS = type(self).SELF_READABLE_FIELDS + user_assignment_readable_fields
        return init_res

    def _compute_user_assignments_count(self):
        assignment_data = self.env['user.assignment'].read_group([('user_id', 'in', self.ids)], ['user_id'], ['user_id'])
        mapped_data = dict([(dict_data['user_id'][0], dict_data['user_id_count']) for dict_data in assignment_data])
        for r in self:
            r.user_assignments_count = mapped_data.get(r.id, 0)

    def action_view_assignments(self):
        action = self.env['ir.actions.act_window']._for_xml_id('viin_user_assignment_log.action_user_assignment')
        action['domain'] = "[('user_id','in',%s)]" % str(self.ids)
        return action

    def unlink(self):
        if self.user_assignment_ids:
            self.user_assignment_ids.sudo().unlink()
        return super(ResUsers, self).unlink()
