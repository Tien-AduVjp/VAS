# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.osv import expression
from odoo.exceptions import AccessDenied, UserError


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    pow_timesheet_required = fields.Boolean(string='PoW Timesheet Required', compute='_compute_pow_timesheet_required',
                                            store=True, tracking=True)
    pow_timesheet_ids = fields.One2many('account.analytic.line', 'pow_for_timeoff_id',
                                        string='PoW Timesheet Entries',
                                        help="The related timesheet entries for PoW (proof of work).")
    pow_timesheet_hours = fields.Float(string='PoW Timesheet Hours', compute='_compute_pow_timesheet_hours', compute_sudo=True,
                                       help="The total actual hours by timesheet recorded as proof of work for the time-off.")

    @api.depends('state', 'holiday_status_id', 'employee_id')
    def _compute_pow_timesheet_required(self):
        for r in self:
            r.pow_timesheet_required = r.holiday_status_id.pow_timesheet_required and r.employee_id.pow_timesheet_required

    @api.depends('pow_timesheet_ids.unit_amount')
    def _compute_pow_timesheet_hours(self):
        total_ts_data = self.env['account.analytic.line'].read_group(
            [('pow_for_timeoff_id', 'in', self.ids)],
            ['pow_for_timeoff_id', 'unit_amount'],
            ['pow_for_timeoff_id']
            )
        mapped_data = dict([(dict_data['pow_for_timeoff_id'][0], dict_data['unit_amount']) for dict_data in total_ts_data])
        for r in self:
            r.pow_timesheet_hours = mapped_data.get(r.id, 0.0)

    def _get_intervals(self, naive=False):
        """
        List leave intervals related to the time off in self

        :param naive: if True, the return datetime will be timzone unaware and considered as UTC

        :return: Returns a dictionary of {
            employee_id: list of tuples (start, stop, hours, resource.calendar.leaves)
            } list of tuples (start, stop, hours, resource.calendar.leaves)
        :rtype: dict
        """
        return self.mapped('employee_id').list_leaves_intervals(
            min(self.mapped('date_from')),
            max(self.mapped('date_to')),
            domain=[('holiday_id', 'in', self.ids)],
            group_by_date=True,
            naive=naive
            )

    def _get_pow_timesheet_candidates_domain(self):
        now = fields.Datetime.now()
        date_from = min(self.mapped('date_from') or [now])
        date_to = max(self.mapped('date_to') or [now])
        return [
            ('project_id', '!=', False),
            ('employee_id', 'in', self.sudo().employee_id.ids),
            ('date', '>=', date_from),
            ('date', '<=', date_to),
            # exclude timesheet that were auto generated for time off
            ('holiday_id', '=', False)
            ]

    def _match_timesheet_for_pow(self):
        pow_ts_required_leaves = self.filtered(lambda l: l.pow_timesheet_required and l.state == 'validate')
        if pow_ts_required_leaves:
            pow_timesheet_candidates_domain = pow_ts_required_leaves._get_pow_timesheet_candidates_domain()
            pow_timesheet_candidates_domain = expression.AND([
                pow_timesheet_candidates_domain,
                [
                    '|',
                    ('pow_for_timeoff_id', '=', False),
                    ('pow_for_timeoff_id', 'in', pow_ts_required_leaves.ids)
                    ]
                ])
            pow_timesheet_candidates = self.env['account.analytic.line'].sudo().search(pow_timesheet_candidates_domain)
            pow_timesheet_candidates._compute_pow_for_timeoff_id()

    def _free_pow_timesheets(self):
        self.pow_timesheet_ids.write({'pow_for_timeoff_id': False})

    def _toggle_pow_timesheet_required(self):
        """ Inverse the value of the field ``pow_timesheet_required`` on the records in ``self``. """
        for r in self:
            if r.pow_timesheet_required:
                if r.holiday_status_id.pow_timesheet_required and r.employee_id.pow_timesheet_required:
                    raise UserError(_("The time off '%s' requires proof of work timesheet as both its type and the employee"
                                      " setting require that. Please disable PoW Timesheet Required option for either"
                                      " of them first.")
                                      % (r.display_name,)
                                      )
            else:
                if not r.holiday_status_id.pow_timesheet_required or not r.employee_id.pow_timesheet_required:
                    raise UserError(_("The time off '%s' does not require proof of work timesheet as either its type or the employee"
                                      " setting does not require that. Please enable PoW Timesheet Required option for both of them"
                                      " first.")
                                      % (r.display_name,)
                                      )
            r.pow_timesheet_required = not r.pow_timesheet_required
        to_free = self.filtered(lambda l: not l.pow_timesheet_required)
        if to_free:
            to_free._free_pow_timesheets()
        to_rematch = (self - to_free).filtered(lambda l: l.state == 'validate')
        if to_rematch:
            to_rematch._match_timesheet_for_pow()

    def action_validate(self):
        res = super(HrLeave, self).action_validate()
        if not self._context.get('do_not_match_timesheet_for_pow', False):
            self._match_timesheet_for_pow()
        return res

    def action_refuse(self):
        res = super(HrLeave, self).action_refuse()
        self._free_pow_timesheets()
        return res

    def action_toggle_pow_timesheet_required(self):
        if not self.env.user.has_group('hr_holidays.group_hr_holidays_user'):
            raise AccessDenied(_("Only users that are granted with the access group '%s' will be able to execute this action.")
                               % self.env.ref('hr_holidays.group_hr_holidays_user').display_name
                               )
        self._toggle_pow_timesheet_required()

    def action_view_pow_timesheet(self):
        action = self.env['ir.actions.act_window']._for_xml_id('hr_timesheet.act_hr_timesheet_line')
        action['domain'] = "[('pow_for_timeoff_id', 'in', %s)]" % self.ids
        return action

    def action_view_pow_timesheet_candidates(self):
        action = self.env['ir.actions.act_window']._for_xml_id('hr_timesheet.act_hr_timesheet_line')
        action['domain'] = self._get_pow_timesheet_candidates_domain()
        return action
