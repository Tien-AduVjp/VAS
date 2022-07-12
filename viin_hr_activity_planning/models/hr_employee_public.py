from odoo import models, fields, api


class HrEmployeePublic(models.Model):
    _name = 'hr.employee.public'
    _inherit = ['hr.employee.public', 'mail.thread', 'mail.activity.mixin']
    _mail_post_access = 'read'

    employee_id = fields.Many2one('hr.employee', readonly=True, compute_sudo=True, compute='_compute_employee')
    activity_ids = fields.One2many(readonly=True, compute_sudo=True, compute='_compute_activities')
    message_follower_ids = fields.One2many(readonly=True, compute_sudo=True, compute='_compute_followers')
    message_ids = fields.One2many(readonly=True, compute_sudo=True, compute='_compute_messages')
    message_main_attachment_id = fields.Many2one(related='employee_id.message_main_attachment_id')

    def _compute_employee(self):
        for r in self:
            r.employee_id = r.id

    @api.depends('employee_id')
    def _compute_activities(self):
        for r in self:
            followers = r.employee_id.message_partner_ids.mapped('user_ids')
            if self.env.user in followers:
                if r.user_id == self.env.user:
                    r.activity_ids = r.employee_id.activity_ids.filtered(lambda act: act.user_id == self.env.user)
                else:
                    r.activity_ids = r.employee_id.activity_ids
            else:
                r.activity_ids = False

    @api.depends('employee_id')
    def _compute_followers(self):
        for r in self:
            r.message_follower_ids = r.employee_id.message_follower_ids

    @api.depends('employee_id')
    def _compute_messages(self):
        for r in self:
            followers = r.employee_id.message_partner_ids.mapped('user_ids')
            if self.env.user in followers:
                if r.user_id == self.env.user:
                    r.message_ids = self.env['mail.message'].search([
                        ('model', '=', 'hr.employee.public'),
                        ('res_id', '=', r.id),
                        ('message_type', '!=', 'user_notification'),
                        ('author_id', '=', self.env.user.partner_id.id)
                    ])
                else:
                    r.message_ids = self.env['mail.message'].search([
                        ('model', '=', 'hr.employee.public'),
                        ('res_id', '=', r.id),
                        ('message_type', '!=', 'user_notification')
                    ])
            else:
                r.message_ids = False
