from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class QualityCheck(models.Model):
    _name = "quality.check"
    _description = "Quality Check"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _mail_post_access = 'read'

    name = fields.Char(string='Name', default=lambda self: _('New'), copy=False)
    control_date = fields.Datetime(string='Control Date', tracking=True)
    point_id = fields.Many2one('quality.point', string='Control Point', tracking=True)
    user_id = fields.Many2one('res.users', string='Responsible', tracking=True, compute='_compute_user_id', readonly=False, store=True)
    title = fields.Char(string='Title', related='point_id.title')
    team_id = fields.Many2one('quality.alert.team', string='Team', required=True, copy=True,
                              compute='_compute_team_id_and_type_id', readonly=False, store=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    alert_ids = fields.One2many('quality.alert', 'check_id', string='Alerts', store=True, index=True)
    test_type = fields.Char(related="point_id.test_type", readonly=True)
    norm_unit = fields.Char(related='point_id.norm_unit', readonly=True)
    measure_success = fields.Selection([
        ('none', 'No measure'),
        ('pass', 'Pass'),
        ('fail', 'Fail')], string="Measure Success", compute="_compute_measure_success",
        readonly=True, store=True)
    quality_state = fields.Selection([
        ('none', 'To do'),
        ('pass', 'Passed'),
        ('fail', 'Failed')], string='Status', tracking=True,
        default='none', copy=False)
    warning_message = fields.Text(compute='_compute_warning_message')
    failure_message = fields.Html(related='point_id.failure_message', readonly=True)
    note = fields.Html(related='point_id.note', readonly=True)
    comment = fields.Text('Comment')
    alert_count = fields.Integer(string='# Quality Alerts', compute="_compute_alert_count", tracking=True)
    measure = fields.Float(string='Measure', default=0.0, digits='Quality Tests', tracking=True)
    tolerance_min = fields.Float(string='Min Tolerance', related='point_id.tolerance_min', readonly=True, store=True)
    tolerance_max = fields.Float(string='Max Tolerance', related='point_id.tolerance_max', readonly=True, store=True)
    norm = fields.Float(string='Norm', related='point_id.norm', readonly=True, store=True)
    type_id = fields.Many2one('quality.type', string='Quality Type', required=True, compute='_compute_team_id_and_type_id',
                              readonly=False, store=True, tracking=True)
    quality_type = fields.Selection(related='type_id.type')

    @api.depends('measure')
    def _compute_measure_success(self):
        for r in self:
            if r.point_id.test_type != 'passfail':
                if r.measure >= r.point_id.tolerance_min and r.measure <= r.point_id.tolerance_max:
                    r.measure_success = 'pass'
                else:
                    r.measure_success = 'fail'
            else:
                r.measure_success = 'none'

    @api.depends('measure_success')
    def _compute_warning_message(self):
        for r in self:
            if r.measure_success == 'fail':
                r.warning_message = _('You measured %.2f %s and it should be between %.2f and %.2f %s.') % (
                    r.measure, r.norm_unit, r.point_id.tolerance_min,
                    r.point_id.tolerance_max, r.norm_unit
                )
            else:
                r.warning_message = ""

    @api.depends('alert_ids')
    def _compute_alert_count(self):
        alert_data = self.env['quality.alert'].read_group([('check_id', 'in', self.ids)], ['check_id'], ['check_id'])
        alert_result = dict((data['check_id'][0], data['check_id_count']) for data in alert_data)
        for r in self:
            r.alert_count = alert_result.get(r.id, 0)

    @api.depends('point_id')
    def _compute_team_id_and_type_id(self):
        for r in self:
            if r.point_id:
                r.team_id = r.point_id.team_id.id
                r.type_id = r.point_id.type_id.id
            else:
                r.team_id = r.team_id
                r.type_id = r.type_id

    @api.depends('point_id')
    def _compute_user_id(self):
        for r in self:
            if r.point_id:
                r.user_id = r.point_id.user_id.id
            else:
                r.user_id = r.user_id

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'name' not in vals or vals['name'] == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('quality.check') or _('New')
        return super(QualityCheck, self).create(vals_list)

    def write(self, vals):
        user = self.env.user
        if not self.env.su and user.has_group('base.group_user') \
                and not user.has_group('to_quality.group_quality_user') \
                and all(r.user_id == user for r in self):
            if set(vals) - set(self._internal_user_whitelist_fields()):
                raise UserError(_("You are not allowed to edit check's information except the following: %s.")
                                % ', '.join([self._fields[f]._description_string(self.env) for f in self._internal_user_whitelist_fields()]))
        return super(QualityCheck, self).write(vals)

    @api.model
    def _internal_user_whitelist_fields(self):
        return ['measure', 'comment']

    def do_measure(self):
        self.ensure_one()
        if self.point_id:
            if self.measure < self.point_id.tolerance_min or self.measure > self.point_id.tolerance_max:
                return {
                    'name': _('Quality Check Failed'),
                    'type': 'ir.actions.act_window',
                    'res_model': 'quality.check',
                    'view_mode': 'form',
                    'view_id': self.env.ref('to_quality.quality_check_view_form_failure').id,
                    'target': 'new',
                    'res_id': self.id,
                    'context': self.env.context,
                }
            return self.do_pass()

    def correct_measure(self):
        self.ensure_one()
        return {
            'name': _('Quality Checks'),
            'type': 'ir.actions.act_window',
            'res_model': 'quality.check',
            'view_mode': 'form',
            'view_id': self.env.ref('to_quality.quality_check_view_form_small').id,
            'target': 'new',
            'res_id': self.id,
            'context': self.env.context,
        }

    def _update_quality_state(self, state):
        user = self.env.user
        vals = {'quality_state': state,
                'user_id': user.id,
                'control_date': datetime.now()}
        # If current user does not have quality rights, we still allow him
        # to mark the check as pass/fail if that check is assigned to him
        if user.has_group('base.group_user') \
                and not user.has_group('to_quality.group_quality_user') \
                and all(r.user_id == user for r in self):
            self.sudo().write(vals)
        else:
            self.write(vals)
        if self._context.get('allow_redirect'):
            return self._redirect_after_pass_fail()

    def do_pass(self):
        return self._update_quality_state('pass')

    def do_fail(self):
        return self._update_quality_state('fail')

    def _prepare_quality_alert_data(self):
        return {
            'check_id': self.id,
            'user_id': self.user_id.id,
            'team_id': self.team_id.id,
            'company_id': self.company_id.id,
            'type_id': self.type_id.id
        }

    def do_alert(self):
        self.ensure_one()
        alert = self.env['quality.alert'].create(self._prepare_quality_alert_data())
        return {
            'name': _('Quality Alert'),
            'type': 'ir.actions.act_window',
            'res_model': 'quality.alert',
            'views': [(self.env.ref('to_quality.quality_alert_view_form').id, 'form')],
            'res_id': alert.id,
            'context': {'default_check_id': self.id},
        }

    def action_view_quality_alerts(self):
        self.ensure_one()
        if len(self.alert_ids) == 1:
            return {
                'name': _('Quality Alert'),
                'type': 'ir.actions.act_window',
                'res_model': 'quality.alert',
                'views': [(self.env.ref('to_quality.quality_alert_view_form').id, 'form')],
                'res_id': self.alert_ids.id,
                'context': {'default_check_id': self.id},
            }
        else:
            action = self.env['ir.actions.act_window']._for_xml_id('to_quality.quality_alert_action_check')
            action['domain'] = [('id', 'in', self.alert_ids.ids)]
            return action

    def _redirect_after_pass_fail(self):
        return {'type': 'ir.actions.act_window_close'}
