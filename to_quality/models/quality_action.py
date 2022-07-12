from odoo import fields, api, models, _


class QualityAction(models.Model):
    _name = "quality.action"
    _description = "Quality Action"
    _inherit = ['mail.thread']

    name = fields.Char('Name', default=lambda self: _('New'), required=True, translate=True, tracking=True)
    description = fields.Html('Description', tracking=True)
    quality_alert_action_ids = fields.One2many('quality.alert.action', 'quality_action_id', string='Quality Alert Actions')
    quality_check_ids = fields.Many2many('quality.check', 'quality_action_quality_check_rel', 'action_id', 'check_id', string='Quality Checks',
                                         compute='_compute_quality_checks', store=True)
    quality_alert_ids = fields.Many2many('quality.alert', 'quality_action_quality_alert_rel', 'action_id', 'alert_id', string='Quality Alerts',
                                         compute='_compute_quality_alerts', store=True)
    user_id = fields.Many2one('res.users', string='Responsible', default=lambda self: self.env.user, tracking=True,
                              help='User who responsible for this quality alert action.')
    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', "The name of the action must be unique!"),
    ]

    @api.depends('quality_alert_action_ids.quality_alert_id.check_id')
    def _compute_quality_check_ids(self):
        for r in self:
            r.quality_check_ids = r.quality_alert_action_ids.mapped('quality_alert_id.check_id')

    @api.depends('quality_alert_action_ids.quality_alert_id')
    def _compute_quality_alert_ids(self):
        for r in self:
            r.quality_alert_ids = r.quality_alert_action_ids.mapped('quality_alert_id')
