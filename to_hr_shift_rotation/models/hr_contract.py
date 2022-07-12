from dateutil import rrule  # Recurrence rule

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class HrContract(models.Model):
    _inherit = 'hr.contract'

    accept_shift_rotation = fields.Boolean(string='Accepted Shift Rotation', default=False)
    rule_id = fields.Many2one('shift.rotation.rule', string='Shift Rotation Rule')
    begin_shift_rotation_rule_line_id = fields.Many2one('shift.rotation.rule.line', string='Begin Rule Line')
    shift_scheduling_line_ids = fields.One2many('shift.scheduling.line', 'contract_id', string='Shift Schedule')
   
    @api.constrains('rule_id','begin_shift_rotation_rule_line_id')
    def _check_shift_rotation_rule(self):
        for r in self:
            if r.accept_shift_rotation:
                if not r.rule_id.line_ids:
                    raise UserError(_("The 'shift rotation rule' %s has no line. Please select another one") % r.rule_id.name)
                if not r.begin_shift_rotation_rule_line_id:
                    raise UserError(_("The 'begin rule line' has no line. Please select another one"))

    @api.onchange('rule_id')
    def _onchange_rule_id(self):
        res = {}
        if self.rule_id:
            res['domain'] = {'begin_shift_rotation_rule_line_id':[('id', 'in', self.rule_id.line_ids.ids)]}
        return res

    def get_resource_calendar(self, dt, state='confirm'):
        self.ensure_one()
        date = fields.Date.to_string(dt)
        if not self.accept_shift_rotation:
            return self.resource_calendar_id
        if not self.shift_scheduling_line_ids:
            return False
        shift_scheduling_line = self.shift_scheduling_line_ids.filtered(lambda rec: rec.date_from <= date and rec.date_to >= date and rec.state == state)
        return shift_scheduling_line and shift_scheduling_line.resource_calendar_id or False

    def _generate_shift_scheduling_lines(self, to_date=None):
        """
        Generate shift scheduling line from contract start date to to_date
        
        @param to_date: the date to which the scheduling lines will be generated
        @type to_date: datetime.date
        """
        for r in self:
            '''
            if not r.rule_id:
                raise UserError(_("The contract %s does not have a shift rotation rule!") % r.name)
            '''
            rule_line_id = r.begin_shift_rotation_rule_line_id or r.rule_id.line_ids[0]

            to_date = to_date or r.date_end or fields.Date.today()
            if r.date_end and to_date > r.date_end:
                to_date = r.date_end

            last_dt = False
            cmd = []
            if r.rule_id.rotating_frequency not in ('quarterly', 'biannually'):
                for dt in rrule.rrule(getattr(rrule.MONTHLY, r.rule_id.rotating_frequency.upper()), dtstart=r.date_start, until=to_date):
                    if not last_dt:
                        last_dt = dt
                        continue
                    data = rule_line_id._prepare_shift_schedule_line_data(r, last_dt.date(), dt.date())
                    cmd.append((0, 0, data))
                    last_dt = dt
                    rule_line_id = rule_line_id.get_next()
            else:
                raise NotImplementedError(_("Rotating frequency 'quarterly' and 'biannually' are not supported yet."))
            r.write({
                'shift_scheduling_line_ids': cmd,
                'begin_shift_rotation_rule_line_id': rule_line_id.id
                })

