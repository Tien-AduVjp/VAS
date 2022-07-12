from odoo import api, fields, models


class QualityAlertAction(models.Model):
    _name = 'quality.alert.action'
    _description = 'Quality Alert Action'
    _rec_name = 'quality_action_id'
    _order = "sequence, id"

    sequence = fields.Integer(string='Sequence', default=10, tracking=True)
    description = fields.Html(string='Description', compute='_compute_description', readonly=False, store=True)
    user_id = fields.Many2one('res.users', string='Responsible', compute='_compute_user_id', readonly=False, store=True,
                              tracking=True, help='User who responsible for this quality alert action.')
    type = fields.Selection([
        ('corrective', 'Corrective'),
        ('preventive', 'Preventive')], index=True, string='Action Type', readonly=True)
    quality_action_id = fields.Many2one('quality.action', string='Action', required=True, tracking=True,
                                        index=True, help='The action to perform')
    quality_alert_id = fields.Many2one('quality.alert', string='Quality Alert', required=True,
                                       index=True, tracking=True, help='Related Quality Alert')
    action_done = fields.Datetime(string='Action time has been complete')
    deadline = fields.Datetime(string='Deadline', required=True, tracking=True, help='Last timeout which action must be finished')
    check_id = fields.Many2one('quality.check', related='quality_alert_id.check_id', readonly=True, index=True)
    product_id = fields.Many2one('product.product', related='quality_alert_id.product_id', store=True, readonly=True, index=True)
    product_tmpl_id = fields.Many2one('product.template', string='Product',
                                      related='quality_alert_id.product_tmpl_id', store=True, readonly=True, index=True)
    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Low'),
        ('2', 'High'),
        ('3', 'Very High')], string='Priority', related='quality_alert_id.priority', store=True, readonly=True,
        index=True)

    @api.depends('quality_action_id', 'quality_alert_id')
    def _compute_user_id(self):
        for r in self:
            if r.quality_action_id:
                r.user_id = r.quality_action_id.user_id
            elif r.quality_alert_id:
                r.user_id = r.quality_alert_id.user_id
            else:
                r.user_id = r.user_id

    @api.depends('quality_action_id')
    def _compute_description(self):
        for r in self:
            if r.quality_action_id:
                r.description = r.quality_action_id.description
            else:
                r.description = r.description
