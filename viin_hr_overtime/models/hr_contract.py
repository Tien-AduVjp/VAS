# -*- coding: utf-8 -*-
import logging

from datetime import datetime, date, time

from odoo import models, fields, api, _

from .res_company import OVERTIME_RECOGNITION_MODE

_logger = logging.getLogger(__name__)


class HrContract(models.Model):
    _inherit = 'hr.contract'

    overtime_recognition_mode = fields.Selection(OVERTIME_RECOGNITION_MODE, string='Overtime Recognition Mode', default=False, tracking=True,
                                            help="This indicates mode to recognize actual overtime against the plan which could be either"
                                            " By Plan or Attendance or Timesheet. Bridging modules will be required to have full"
                                            " options accordingly.\n"
                                            "If this field is left empty, the value will be taken from the corresponding company's settings.")
    overtime_plan_line_ids = fields.One2many('hr.overtime.plan.line', 'contract_id', string='Overtime Plan Lines')
    overtime_plans_count = fields.Integer(compute='_compute_overtime_plans_count', compute_sudo=True)
    overtime_base_mode = fields.Selection([
        ('manual', 'Manual Input'),
        ('wage', 'Basic Wage')],
        string='Overtime Base Mode',
        default='wage', required=True, tracking=True,
        help="The overtime base mode for overtime pay computation.\n"
        "* Manual Input: you can define any base amount below manually;\n"
        "* Basic Wage: the base amount will be the contract's basic wage;\n")
    overtime_base_amount = fields.Monetary(string='Overtime Base Amount', compute='_compute_overtime_base_amount', store=True,
                                           readonly=False, tracking=True,
                                           help="The monthly base amount that will be used in overtime pay computation.")
    mismatched_overtime_plan_ids = fields.Many2many('hr.overtime.plan', 'hr_contract_overtime_plan_mismatch_rel', 'contract_id', 'plan_id',
                                                    string='Mismatched Overtime Plans',
                                                    compute='_compute_mismatched_overtime_plans', store=True,
                                                    help="Contains the overtime plans that have date range outside the current contract.")

    @api.depends('overtime_base_mode', 'wage')
    def _compute_overtime_base_amount(self):
        for r in self:
            r.overtime_base_amount = r._get_overtime_base_amount()

    @api.depends('employee_id', 'date_start', 'date_end', 'state', 'overtime_plan_line_ids.date_start', 'overtime_plan_line_ids.date_end')
    def _compute_mismatched_overtime_plans(self):
        for r in self:
            if r.state not in ('open', 'close'):
                r.mismatched_overtime_plan_ids = False
            else:
                r.mismatched_overtime_plan_ids = [(6, 0, r._get_mismatched_overtime_plans().ids)]

    def _compute_overtime_plans_count(self):
        for r in self:
            r.overtime_plans_count = len(r.overtime_plan_line_ids.overtime_plan_id)

    def action_start_contract(self):
        super(HrContract, self).action_start_contract()
        self.mismatched_overtime_plan_ids.action_resolve_contract_mismatch()

    def action_cancel(self):
        super(HrContract, self).action_cancel()
        self.overtime_plan_line_ids.overtime_plan_id.action_resolve_contract_mismatch()

    def action_view_mismatched_overtime_plans(self):
        result = self.env['ir.actions.actions']._for_xml_id('viin_hr_overtime.action_hr_overtime_plan')
        result['domain'] = "[('id','in',%s)]" % str(self.mismatched_overtime_plan_ids.ids)
        return result

    def action_view_overtime_plans(self):
        result = self.env['ir.actions.actions']._for_xml_id('viin_hr_overtime.action_hr_overtime_plan')
        result['domain'] = "[('id','in',%s)]" % str(self.overtime_plan_line_ids.overtime_plan_id.ids)
        return result

    def _get_mismatched_overtime_plans(self):
        mismatched = self.env['hr.overtime.plan']
        for r in self.filtered(lambda c: c.date_end):
            mismatched |= r.overtime_plan_line_ids.filtered(
                lambda l: l.date_end > datetime.combine(r.date_end, time.max) \
                or l.date_end < datetime.combine(r.date_start, time.min)
                ).overtime_plan_id

        candidates = self.env['hr.overtime.plan'].search(self._prepare_related_overtime_plan_domain())
        for r in self:
            mismatched |= candidates.filtered(
                lambda l: l.employee_id.id == r.employee_id.id \
                and l.date_start < datetime.combine(r.date_end or date(9990, 12, 31), time.max) \
                and l.date_end > datetime.combine(r.date_start, time.min) \
                and l.id not in r.overtime_plan_line_ids.overtime_plan_id.ids
                )
        return mismatched

    def _sorted_contracts(self, reverse=False):
        return self.sorted(lambda c: (c.date_start, c.date_end or date(9990, 12, 31)), reverse=reverse)

    def _get_overtime_intervals(self, ot_start_dt, ot_end_dt):
        res = {}
        unavailable_intervals = self._get_unavailable_intervals(ot_start_dt, ot_end_dt, naive_datetime=True)
        for contract, calendar_map in unavailable_intervals.items():
            res.setdefault(contract, {})
            for res_cal, intervals in calendar_map.items():
                res[contract].setdefault(res_cal, {})
                for interval in intervals:
                    if not interval:
                        continue
                    res[contract][res_cal].update(
                        res_cal._match_overtime_rules(interval[0], interval[1], company=self.company_id)
                        )
        return res

    def _get_overtime_recognition_mode(self):
        return self.overtime_recognition_mode or self.company_id.overtime_recognition_mode

    def _prepare_related_overtime_plan_domain(self):
        sorted_contracts = self._sorted_contracts()
        return [
            ('employee_id', 'in', self.employee_id.ids),
            ('date_start', '<', datetime.combine(sorted_contracts[-1:].date_end or date(9990, 12, 31), time.max)),
            ('date_end', '>', datetime.combine(sorted_contracts[:1].date_start, time.min)),
            ]

    def _prepare_overtime_plan_line_vals(self, overtime_plan):
        self.ensure_one()

        recognition_mode = overtime_plan.recognition_mode or self._get_overtime_recognition_mode()
        # if not recognition_mode:
        #     raise ValidationError(_("No overtime recognition mode found. Please specify one either in your overtime"
        #                             " planning entry or in the corresponding contract or in the company's settings."))
        unavailable_intervals = self._get_overtime_intervals(overtime_plan.date_start, overtime_plan.date_end)
        vals_list = []
        for contract, calendar_map in unavailable_intervals.items():
            for res_cal, intervals in calendar_map.items():
                for interval, ot_rule in intervals.items():
                    vals_list.append({
                        'overtime_plan_id': overtime_plan.id,
                        'contract_id': contract.id,
                        'resource_calendar_id': res_cal.id,
                        'date_start': interval[0],
                        'date_end': interval[1],
                        'global_leave_id': interval[2] and interval[2].id or False,
                        'hr_overtime_rule_id': ot_rule.id,
                        'rule_code_id': ot_rule.code_id.id,
                        'tz': res_cal.tz or self._context.get('tz'),
                        'recognition_mode': recognition_mode,
                        'standard_hour_pay': self._get_overtime_standard_hour_pay(interval[0], interval[1]),
                        'pay_rate': ot_rule.pay_rate,
                        })
        return vals_list

    def _get_standard_hour_pay(self, date_start, date_end):
        # TODO: remove me in master/14+
        _logger.warning("The method `_get_standard_hour_pay()` is deprecated. Please use the `_get_overtime_standard_hour_pay()` instead.")
        return self._get_overtime_standard_hour_pay(date_start, date_end)

    def _get_overtime_standard_hour_pay(self, date_start, date_end):
        """
        Method to get standard hour pay which is calculated based on the contract's Overtime Base Amount and
        the normal work hours in month (without global leaves and abnormal working time)
        """
        self.ensure_one()
        return self.overtime_base_amount / self._get_work_hours_in_month(
            date_start,
            date_end,
            global_leaves=False,  # we don't want global leaves
            employee_leaves=False,
            global_attendances_only=True,  # we don't want abnormal attendances
            )

    def _get_month_cycle_start_end(self, date_start=None, date_end=None):
        now = fields.Datetime.now()
        date_start = date_start or now
        date_end = date_end or now
        date_start = fields.Datetime.start_of(date_start, 'month')
        date_end = fields.Datetime.end_of(date_end, 'month')
        return date_start, date_end

    def _get_work_hours_in_month(self, date_start, date_end, global_leaves=True, employee_leaves=False, global_attendances_only=False):
        self.ensure_one()
        # The given date_start and date_end being passed in this method is at UTC
        # while the contract's dates (coming without time) are accepted as at contract's calendar timezone)
        # Converting the given dates at UTC into the dates at contract's calendar's timezone is required
        contract_tz = self.resource_calendar_id.tz or self.employee_id.tz or 'UTC'
        date_start = self.env['to.base'].convert_utc_time_to_tz(date_start, tz_name=contract_tz).replace(tzinfo=None)
        date_end = self.env['to.base'].convert_utc_time_to_tz(date_end, tz_name=contract_tz).replace(tzinfo=None)
        date_start, date_end = self._get_month_cycle_start_end(date_start, date_end)
        hours = 0.0
        for r in self:
            for start, end, _ in r.employee_id._get_work_intervals(
                date_start,
                date_end,
                naive_datetime=True,
                global_leaves=global_leaves,
                employee_leaves=employee_leaves,
                global_attendances_only=global_attendances_only,
                )[r.employee_id.id]:
                hours += (end - start).total_seconds() / 3600
        return hours

    def _get_overtime_base_amount(self):
        """
        Hooking method for others to extend that may add more factor to the overtime base
        """
        return self.wage
