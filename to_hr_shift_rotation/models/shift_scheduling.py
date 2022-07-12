from datetime import datetime

from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
from odoo.exceptions import ValidationError, UserError
from odoo.tools import format_date


class ShiftScheduling(models.Model):
    _name = 'shift.scheduling'
    _description = 'Shift Schedule'

    line_ids = fields.One2many('shift.scheduling.line', 'schedule_id', string='Lines')


class ShiftRotationLine(models.Model):
    _name = 'shift.scheduling.line'
    _description = 'Shift Schedule Line'
    _order = 'date_from DESC'
    _inherit = ['mail.thread']

    schedule_id = fields.Many2one('shift.scheduling')
    date_from = fields.Date(string='Date From', required=True, index=True)
    date_to = fields.Date(string='Date To', required=True, index=True)
    resource_calendar_id = fields.Many2one('resource.calendar', string='Working Schedule', required=True, index=True)
    employee_id = fields.Many2one('hr.employee', store=True, string='Employee', required=True, index=True)
    contract_id = fields.Many2one('hr.contract', string='Contract', store=True, required=True, index=True,
                                  domain="[('id','in',employee_id.contract_ids)]")
    rate = fields.Float(string='Rate (%)', required=True, default=100.0,
                        help='The extra pay in percentage (of basic wage, for example) which can be used in payroll computation.')
    shift_rotation_rule_line_id = fields.Many2one('shift.rotation.rule.line', string='Rule Line', index=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('cancel', 'Canceled'),
    ], string="Status", tracking=True, required=True, default='draft')

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        # TODO: convert this to compute
        if self.employee_id and self.employee_id.contract_id:
            self.contract_id = self.employee_id.contract_id

    @api.constrains('date_from', 'date_to', 'employee_id')
    def _check_dates(self):
        for r in self:
            if r.date_from:
                weekday_from = datetime.strptime(r.date_from + ' 00:00:00', DTF).weekday()
                if weekday_from != 0:
                    raise ValidationError(_('Date from must on Monday'))
            if r.date_to:
                weekday_to = datetime.strptime(r.date_to + ' 00:00:00', DTF).weekday()
                if weekday_to != 6:
                    raise ValidationError(_('Date to must on Sunday'))
            if r.date_from and r.date_to:
                days = (datetime.strptime(r.date_to + ' 00:00:00', DTF) - datetime.strptime(r.date_from + ' 00:00:00', DTF)).days
                if days <= 0:
                    raise ValidationError(_('Date to must greater than date from'))
                elif days > 7:
                    raise ValidationError(_('Date from and date to must in the same week'))
                if r.employee_id:
                    srl = self.env['shift.scheduling.line'].search([('date_from', '=', r.date_from),
                                                                  ('date_to', '=', r.date_to),
                                                                  ('employee_id', '=', r.employee_id.id)])
                    if len(srl) > 1:
                        raise ValidationError(_('The shift rotation line for employee %s are overlapped') % r.employee_id.name)

    def action_confirm(self):
        self.write({'state':'confirm'})

    def action_draft(self):
        self.write({'state':'draft'})

    def action_cancel(self):
        self.write({'state':'cancel'})

    def unlink(self):
        for item in self:
            if item.state not in ('draft', 'cancel'):
                raise UserError(_("You can only delete records whose state is draft or canceled."))
        return super(ShiftRotationLine, self).unlink()

    @api.onchange('date_from', 'date_to', 'employee_id')
    def _onchange_date_from_date_to(self):
#         self.validate_data(self.date_from, self.date_to, self.employee_id)
        if self.date_from and self.date_to and self.employee_id:
            contract_ids = self.env['hr.payslip'].get_contract(self.employee_id, self.date_from, self.date_to)
            if not contract_ids:
                return
            contract_id = self.env['hr.contract'].browse(contract_ids[0])
            self.contract_id = contract_id

    def name_get(self):
        result = []
        for r in self:
            result.append((r.id, '[%s] [%s - %s] [%s]' % (r.employee_id.name, format_date(r.env, r.date_from), format_date(r.env, r.date_to), r.resource_calendar_id.name)))
        return result

