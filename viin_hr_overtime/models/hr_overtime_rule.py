from datetime import datetime, time
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.osv import expression
from odoo.tools.date_utils import relativedelta


class HrOvertimeRule(models.Model):
    _name = 'hr.overtime.rule'
    _inherit = ['mail.thread', 'to.base']
    _description = "Overtime Rule"
    _order = 'holiday, weekday ASC, hour_from ASC, id'

    DOW = [
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday')
        ]

    name = fields.Char(string='Name', required=True, translate=True, tracking=True)
    weekday = fields.Selection(DOW, string='Day of Week', required=True, index=True, tracking=True)
    hour_from = fields.Float(string='Start Time', tracking=True, required=True,
                             help="Start time of overtime working")
    hour_to = fields.Float(string='End Time', tracking=True, required=True,
                           help="End time of overtime working")
    holiday = fields.Boolean(string='Holiday', compute='_compute_holiday', store=True, readonly=False,
                              help="If enabled, this indicates the rule is for overtime in holidays")
    code_id = fields.Many2one('hr.overtime.rule.code', required=True, tracking=True, string='Rule Code',
                              help="The predefined code to be used in overtime payroll computation")

    code = fields.Char(string='Code', related='code_id.name', readonly=True)
    pay_rate = fields.Float(string='Pay Rate', compute='_compute_pay_rate', store=True, readonly=False)

    company_id = fields.Many2one('res.company', string='Company', tracking=True, required=True,
                                 default=lambda self: self.env.company,
                                 help="If a company is set, this rule will be valid for the selected company only")

    _sql_constraints = [
        ('date_check', "CHECK (hour_from < hour_to)", "The Start Time must be anterior to the End Time."),
        ('hour_from_check', "CHECK (hour_from >= 0 and hour_from < 24)", "Hour From must be greater than or equal to 0 and less than 24"),
        ('hour_to_check', "CHECK (hour_to > 0 and hour_to <= 24)", "Hour To must be greater than 0 and less than or equal to 24"),
    ]

    def name_get(self):
        return [(rule.id, '%s%s (%s - %s)' % ('[%s] ' % rule.code, rule.name, rule.hours_time_string(rule.hour_from), rule.hours_time_string(rule.hour_to)))
                for rule in self]

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        """
        name search that supports searching by rule and code and times
        """
        args = args or []
        domain = []
        if name:
            domain = ['|', ('code', '=ilike', name + '%'), ('name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&'] + domain
        rules = self.search(domain + args, limit=limit)
        return rules.name_get()

    @api.depends('code_id','code_id.pay_rate')
    def _compute_pay_rate(self):
        for r in self:
            r.pay_rate = r.code_id.pay_rate

    @api.depends('code_id','code_id.holiday')
    def _compute_holiday(self):
        for r in self:
            r.holiday = r.code_id.holiday

    @api.constrains('weekday', 'hour_from', 'hour_to', 'company_id')
    def _overlapping_check(self):
        for r in self:
            overlap = self.search(r._prepare_overlapping_check_domain(), limit=1)
            if overlap:
                raise UserError(_("You have entered an interval that is overlapping the interval of an existing rule (%s)!")
                                % (overlap.name,))

    def _prepare_overlapping_check_domain(self):
        self.ensure_one()
        return [
            ('id', '!=', self.id),
            ('weekday', '=', self.weekday),
            ('holiday', '=', self.holiday),
            ('hour_from', '<', self.hour_to),
            ('hour_to', '>', self.hour_from),
            ('company_id', '=', self.company_id.id),
            ]

    def _get_overtime_interval(self, ot_start, ot_end):
        """
        Return the modified ot_start, ot_end that match the rule
        """
        self.ensure_one()
        if ot_start >= ot_end:
            raise ValidationError(_("The overtime start date must be earlier than the overtime end date."
                                    " This could be a programming error that produced %s and %s") 
                                    % (ot_start, ot_end))
        float_hours_to_time = self.env['to.base'].float_hours_to_time
        rule_start_date = datetime.combine(ot_start.date(), float_hours_to_time(self.hour_from))
        if self.hour_to >= 24:
            rule_end_date = datetime.combine(ot_start.date() + relativedelta(days=+1), time.min)
        else:
            rule_end_date = datetime.combine(ot_start.date(), float_hours_to_time(self.hour_to))
        if ot_start < rule_start_date:
            ot_start = rule_start_date
        if ot_start > rule_end_date:
            ot_start = rule_end_date

        if ot_end < rule_start_date:
            ot_end = rule_start_date
        if ot_end > rule_end_date:
            ot_end = rule_end_date
        return ot_start, ot_end
        
