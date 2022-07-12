from odoo import api, fields, models, _, SUPERUSER_ID


class QualityAlert(models.Model):
    _name = "quality.alert"
    _description = "Quality Alert"
    _inherit = ['mail.thread']
    _mail_post_access = 'read'

    name = fields.Char(string='Name', default=lambda self: _('New'), translate=True, copy=False)
    description = fields.Text('Description')
    stage_id = fields.Many2one('quality.alert.stage', string='Stage',
        group_expand='_read_group_stage_ids', copy=False,
        default=lambda self: self.env['quality.alert.stage'].search([], order='sequence asc', limit=1).id)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    user_id = fields.Many2one('res.users', string='Responsible', tracking=True, default=lambda self: self.env.user)
    team_id = fields.Many2one(
        'quality.alert.team', string='Team', required=True,
        default=lambda x: x.env['quality.alert.team'].search([], limit=1))
    partner_id = fields.Many2one('res.partner', string='Vendor')
    check_id = fields.Many2one('quality.check', string='Check')
    reason_id = fields.Many2one('quality.reason', string='Root Cause')
    tag_ids = fields.Many2many('quality.tag', string="Tags")
    date_assign = fields.Datetime(string='Date Assigned')
    date_close = fields.Datetime(string='Date Closed')
    action_corrective_ids = fields.One2many('quality.alert.corrective.action', 'quality_alert_id',
                                             string='Corrective Actions')
    action_preventive_ids = fields.One2many('quality.alert.preventive.action', 'quality_alert_id',
                                             string='Preventive Actions')
    no_of_corrective_action = fields.Integer(string="# of Corrective Actions", compute='_compute_no_of_corrective_action', store=True)
    no_of_preventive_action = fields.Integer(string="# of Preventive Actions", compute='_compute_no_of_preventive_action', store=True)
    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Low'),
        ('2', 'High'),
        ('3', 'Very High')], string='Priority',
        index=True)
    type_id = fields.Many2one('quality.type', string='Quality Type', required=True, compute='_compute_type_id',
                              readonly=False, store=True, tracking=True)
    quality_type = fields.Selection(related='type_id.type')

    @api.depends('check_id')
    def _compute_type_id(self):
        for r in self:
            if r.check_id:
                r.type_id = r.check_id.type_id.id
            else:
                r.type_id = r.type_id

    @api.depends('action_corrective_ids')
    def _compute_no_of_corrective_action(self):
        for r in self:
            r.no_of_corrective_action = len(r.action_corrective_ids)

    @api.depends('action_preventive_ids')
    def _compute_no_of_preventive_action(self):
        for r in self:
            r.no_of_preventive_action = len(r.action_preventive_ids)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            quality_alert_name = vals.get('name', _('New'))
            if quality_alert_name == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('quality.alert') or _('New')
        return super(QualityAlert, self).create(vals_list)

    def write(self, vals):
        res = super(QualityAlert, self).write(vals)
        if 'stage_id' in vals and self.mapped('stage_id').done:
            self.write({'date_close': fields.Datetime.now()})
        return res

    def action_view_quality_check(self):
        return {
            'name': _('Quality Check'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'quality.check',
            'target': 'current',
            'res_id': self.check_id.id,
        }

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        """ Display all the stages of the ECO type
        in the Kanban view, even without an ECO during that period
        """
        stage_ids = stages._search([], order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)

    @api.model
    def message_new(self, msg_dict, custom_values=None):
        """ Use override with creation by email alias.
        Target: Use the subject for description and not for the name.
        """
        # We need to add the name in custom_values or it will use the subject.
        custom_values['name'] = self.env['ir.sequence'].next_by_code('quality.alert') or _('New')
        subject = msg_dict.get('subject', ''),
        custom_values['description'] = subject
        custom_values['type_id'] = self.env.ref('to_quality.quality_type_general').id
        return super(QualityAlert, self).message_new(msg_dict, custom_values)
