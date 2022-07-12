from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ShiftRotationRule(models.Model):
    _name = 'shift.rotation.rule'
    _description = "Shift Rotation Rule"

    name = fields.Char(string='Name', required=True, translate=True)
    line_ids = fields.One2many('shift.rotation.rule.line', 'rule_id', string='Rule Lines')
    rotating_frequency = fields.Selection([
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('biannually', 'Biannually'),
        ('yearly', 'Yearly')], string='Rotating Frequency', default='weekly', required=True)
    contract_ids = fields.One2many('hr.contract', 'rule_id', string='Contracts')

'''
    def write(self, vals):
        if 'line_ids' in vals and not vals['line_ids']:
            for r in self:
                if r.contract_ids:
                    raise UserError(_("Could not remove lines from the rule %s while the rule is still referred by the contract %s")
                                    % (r.name, r.contract_ids[0].name))
        return super(ShiftRotationRuleLine, self).write(vals)
'''


class ShiftRotationRuleLine(models.Model):
    _name = 'shift.rotation.rule.line'
    _order = 'sequence ASC, id ASC'
    _rec_name = 'resource_calendar_id'
    _description = "Shift Rotation Rule Line"

    resource_calendar_id = fields.Many2one('resource.calendar', string='Working Schedule', required=True,)
    sequence = fields.Integer(string='Sequence', default=1, required=True)
    rule_id = fields.Many2one('shift.rotation.rule', string='Rule', required=True, ondelete="cascade")
    rate = fields.Float(string='Rate (%)', required=True, default=100.0,
                        help='The extra pay in percentage (of basic wage, for example) which can be used in payroll computation.')

    def get_next(self):
        """
        Get the next rule line of the current line

        @return: shift.rotation.rule.line record if found, otherwise return False
        """
        self.ensure_one()
        current_found = False
        for line in self.rule_id.line_ids:
            if current_found:
                return line
            elif line == self:
                current_found = True
        return self.rule_id.line_ids[0]

    def get_previous(self):
        """
        Get the previous rule line of the current line

        @return: shift.rotation.rule.line record if found, otherwise return False
        """
        self.ensure_one()
        last = False
        for line in self.rule_id.line_ids:
            if line == self:
                return last
            last = line
        return self.rule_id.line_ids[-1]

    def _prepare_shift_schedule_line_data(self, contract, date_from, date_to):
        return {
            'date_from': fields.Date.to_string(date_from),
            'date_to':fields.Date.to_string(date_to),
            'resource_calendar_id': self.resource_calendar_id.id,
            'employee_id': contract.employee_id.id,
            'contract_id': contract.id,
            'shift_rotation_rule_line_id': self.id,
            'state': 'draft'
            }

    def get_working_hours_and_rate(self, last_resource_calendar):
        new_working_hours = False
        rate = 0
        i = 0
        for line in self:
            if not last_resource_calendar:
                new_resource_calendar_id = line.resource_calendar_id
                rate = line.rate
                return new_resource_calendar_id, rate
            else:
                if last_resource_calendar.id == line.resource_calendar_id.id:
                    if i == (len(self) - 1):
                        new_resource_calendar_id = self[0].resource_calendar_id
                        rate = self[0].rate
                    else:
                        new_resource_calendar_id = self[i + 1].resource_calendar_id
                        rate = self[i + 1].rate
                    return new_resource_calendar_id, rate
                i += 1
        return new_resource_calendar_id, rate

    def unlink(self):
        rules = self.mapped('rule_id')
        res = super(ShiftRotationRuleLine, self).unlink()
        for rule in rules.filtered(lambda r: not r.line_ids and r.contract_ids):
            raise UserError(_("Could not delete all rule lines of the rule %s while the rule is still referred by the contract %s")
                            % (rule.name, rule.contract_ids[0].name))
        return res

