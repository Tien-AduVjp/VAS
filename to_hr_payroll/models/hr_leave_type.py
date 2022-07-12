import re

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class HrLeaveType(models.Model):
    _name = 'hr.leave.type'
    _inherit = ['hr.leave.type', 'mail.thread']

    # override
    unpaid = fields.Boolean(tracking=True)
    code = fields.Char(compute='_compute_code', store=True, readonly=False, tracking=True,
                       help="The code of the Time Off Type which can be used for Python code in salary rules."
                       " For example, if you have a Legal Leave Type with code of LEGALLEAVE, you can get"
                       " number of left days with the formula `result=worked_days.LEGALLEAVE.number_of_days`"
                       )

    def _get_payslip_protected_fields(self):
        """
        Return a dict of protected fields (field -> label) that are protected from modification
        if the time of type is stilled referred by a payslip
        
        @return: dict (field_1 -> label_1, field_2 -> label_2, ..., field_n -> label_n)
        """
        return {
            'unpaid': _("Unpaid"),
            }

    def write(self, vals):
        protected_fields = self._get_payslip_protected_fields()
        payslip_leave_interval_obj = self.env['payslip.leave.interval']
        for field, label in protected_fields.items():
            if field in vals:
                for r in self:
                    if getattr(r, field) == vals[field]:
                        continue
                    payslip_leave_interval = payslip_leave_interval_obj.search([('holiday_status_id', '=', r.id)], limit=1)
                    payslip = payslip_leave_interval.working_month_calendar_line_id.working_month_calendar_id.payslip_id
                    if payslip_leave_interval:
                        raise UserError(_("You may not be able to modify the value of the field \"%s\" of the Time Off Type \"%s\" while it is still"
                                          " referred by the payslip \"%s\".\nInstead, you could either delete the payslip or define a new Time Off Type"
                                          " (e.g. for another period).")
                                          % (label, r.name, payslip.name)
                                          )
        return super(HrLeaveType, self).write(vals)

    @api.constrains('code')
    def _check_code_validity(self):
        for r in self:
            if r.code and not r.code.isidentifier():
                raise ValidationError(_("The Payroll Code \"%s\" is not a valid code. A valid code may contain alphanumeric and underscore only.") % (r.code,))

    @api.depends('name')
    def _compute_code(self):
        for r in self:
            code = False
            if r.name:
                code = self.env['to.base'].strip_accents(r.name)
                code = re.sub(r'\W+', '', code)  # remove non-word characters
                code = re.sub(r'^[^a-zA-Z]', '', code)  # remove non-letter characters at start of string
            r.code = code
