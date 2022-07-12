import random

from math import sqrt
from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
from odoo.osv import expression
from odoo.exceptions import UserError


class QualityPoint(models.Model):
    _name = "quality.point"
    _description = "Quality Point"
    _inherit = ['mail.thread']
    _order = "sequence, id"

    def _get_default_team_id(self):
        return self.env['quality.alert.team'].search([], limit=1).id

    name = fields.Char(string='Reference', copy=False, default=lambda self: _('New'),
        readonly=True, required=True)
    sequence = fields.Integer('Sequence')
    title = fields.Char(string='Title')
    team_id = fields.Many2one(
        'quality.alert.team', string='Team',
        default=lambda self: self._get_default_team_id(), required=True, tracking=True)
    measure_frequency_type = fields.Selection([
        ('all', 'All Operations'),
        ('random', 'Randomly'),
        ('periodical', 'Periodically')], string="Frequency",
        default='all', required=True, tracking=True)
    measure_frequency_value = fields.Float('Percentage')
    measure_frequency_unit_value = fields.Integer('Frequency Value')
    measure_frequency_unit = fields.Selection([
        ('day', 'Day(s)'),
        ('week', 'Week(s)'),
        ('month', 'Month(s)')], default="day")
    no_proceed_if_failed = fields.Boolean(string='No Proceed if Failed',
                                          help="If quality check fails, the goods will be blocked.")
    norm = fields.Float('Norm', digits='Quality Tests')
    tolerance_min = fields.Float(string='Min Tolerance', digits='Quality Tests')
    tolerance_max = fields.Float(string='Max Tolerance', digits='Quality Tests', compute='_compute_tolerance_max', readonly=False, store=True)
    norm_unit = fields.Char(string='Unit of Measure', default=lambda self: 'mm')
    note = fields.Html(string='Note')
    reason = fields.Html(string='Reason')
    average = fields.Float(compute="_compute_average")
    failure_message = fields.Html(string='Failure Message')
    standard_deviation = fields.Float(compute="_compute_standard_deviation")
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    user_id = fields.Many2one('res.users', string='Responsible', tracking=True)
    active = fields.Boolean(default=True)
    check_count = fields.Integer(compute="_compute_check_count")
    check_ids = fields.One2many('quality.check', 'point_id', string='Quality Checks')
    test_type_id = fields.Many2one('quality.point.test_type', string='Test Type', required=True,
            default=lambda self: self.env['quality.point.test_type'].search([('technical_name', '=', 'passfail')]), tracking=True)
    test_type = fields.Char(related='test_type_id.technical_name', readonly=True)
    type_id = fields.Many2one('quality.type', string='Quality Type', required=True, tracking=True)
    quality_type = fields.Selection(related='type_id.type')

    def _calculate_average(self):
        self.ensure_one()
        if self.test_type != 'measure':
            return 0.0
        else:
            return sum(self.check_ids.mapped('measure')) / len(self.check_ids) if self.check_ids else 0.0

    def _compute_average(self):
        for r in self:
            r.average = r._calculate_average()

    def _compute_standard_deviation(self):
        # Ref.:
        # 1. https://hainguyendt.wordpress.com/2018/10/24/kiem-soat-quy-trinh-bang-phuong-phap-thong-ke-spc/
        # 2. https://www.khanacademy.org/math/statistics-probability/summarizing-quantitative-data/variance-standard-deviation-population/a/calculating-standard-deviation-step-by-step
        for r in self:
            checks_count = len(r.check_ids)
            if r.test_type != 'measure' or checks_count <= 1:
                r.standard_deviation = 0.0
            else:
                average = r._calculate_average()
                s = sum((m - average) ** 2 for m in r.check_ids.mapped('measure'))
                r.standard_deviation = sqrt(s / (checks_count - 1))

    def _compute_check_count(self):
        check_data = self.env['quality.check'].read_group([('point_id', 'in', self.ids)], ['point_id'], ['point_id'])
        dict = {}
        for d in check_data:
            dict[d['point_id'][0]] = d['point_id_count']
        for r in self:
            r.check_count = dict.get(r.id, 0)

    @api.depends('norm')
    def _compute_tolerance_max(self):
        for r in self:
            if r.tolerance_max == 0.0:
                r.tolerance_max = r.norm
            else:
                r.tolerance_max = r.tolerance_max

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'name' not in vals or vals['name'] == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('quality.point') or _('New')
        return super(QualityPoint, self).create(vals_list)

    def unlink(self):
        for r in self:
            if r.check_ids:
                raise UserError(_("You cannot delete a quality point which has been assigned with a quality check. If possible, archive it instead."))
        return super(QualityPoint, self).unlink()

    def action_see_quality_checks(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('to_quality.quality_check_action_main')
        action['domain'] = [('point_id', '=', self.id)]
        action['context'] = {'default_point_id': self.id}
        return action

    def action_see_spc_control(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('to_quality.quality_check_action_spc')
        if self.test_type == 'measure':
            action['context'] = {'group_by': ['name', 'point_id'], 'graph_measure': ['measure'], 'graph_mode': 'line'}
        action['domain'] = [('point_id', '=', self.id), ('quality_state', '!=', 'none')]
        return action

    def check_execute_now(self):
        # @TODO make true multi
        self.ensure_one()
        if self.measure_frequency_type == 'all':
            return True
        elif self.measure_frequency_type == 'random':
            if not self.measure_frequency_value:
                raise UserError(_("Please double-check that the frequency value in the quality point %s is valid.", self.name))
            return (random.random() < self.measure_frequency_value / 100.0)
        elif self.measure_frequency_type == 'periodical':
            if not self.measure_frequency_unit_value or not self.measure_frequency_unit:
                raise UserError(_("Please double-check that the frequency value in the quality point %s is valid.", self.name))
            delta = False
            if self.measure_frequency_unit == 'day':
                delta = relativedelta(days=self.measure_frequency_unit_value)
            elif self.measure_frequency_unit == 'week':
                delta = relativedelta(weeks=self.measure_frequency_unit_value)
            elif self.measure_frequency_unit == 'month':
                delta = relativedelta(months=self.measure_frequency_unit_value)
            date_previous = datetime.today() - delta
            checks = self.env['quality.check'].search([
                ('point_id', '=', self.id),
                ('create_date', '>=', date_previous.strftime(DTF))], limit=1)
            return not checks
        return False

    def name_get(self):
        """
        display combination of name and title
        """
        result = []
        for r in self:
            name = '[%s] %s' % (r.name, r.title) if r.title else r.name
            result.append((r.id, name))
        return result

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        """
        search by name or title
        """
        args = args or []
        domain = []
        if name:
            domain = ['|', ('name', '=ilike', name + '%'), ('name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&'] + domain
        state = self.search(domain + args, limit=limit)
        return state.name_get()
