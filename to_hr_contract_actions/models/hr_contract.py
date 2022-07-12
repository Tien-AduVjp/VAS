from datetime import date
from dateutil.relativedelta import relativedelta

from odoo import api, models, fields, _
from odoo.exceptions import UserError, ValidationError


class HrContract(models.Model):
    _inherit = 'hr.contract'

    state = fields.Selection(help="The Status of the contract which is either:\n"
                             "New: The contract is a draft contract which may not visible in payslip.\n"
                             "Running: the contract is valid and running. It will be available in other processes in the system.\n"
                             "To Renew: the contract will be set to this status automatically when its End Date is between tomorrow"
                             " and the next 7 days, OR its employee's Visa Expire Date is between tomorrow and the next 60 days\n"
                             "Expired: The contract will be set to this status automatically when its End Date or its employee's"
                             " Visa Expire Date is earlier or equal to tomorrow.")

    @api.model
    def update_state(self):
        """
        Override the Odoo's native method in hr_contract module to call action instead of write directly
        # TODO: find a way to call super or any other better way to avoid this dirty hack
        """
        self.search([
            ('state', '=', 'open'),
            '|',
            '&',
            ('date_end', '<=', fields.Date.to_string(date.today() + relativedelta(days=7))),
            ('date_end', '>=', fields.Date.to_string(date.today() + relativedelta(days=1))),
            '&',
            ('visa_expire', '<=', fields.Date.to_string(date.today() + relativedelta(days=60))),
            ('visa_expire', '>=', fields.Date.to_string(date.today() + relativedelta(days=1))),
        ]).action_to_renew()

        self.search([
            ('state', '=', 'open'),
            '|',
            ('date_end', '<=', fields.Date.to_string(date.today() + relativedelta(days=1))),
            ('visa_expire', '<=', fields.Date.to_string(date.today() + relativedelta(days=1))),
        ]).set_as_close()

        self.search([
            ('state', '=', 'draft'),
            ('kanban_state', '=', 'done'),
            ('date_start', '<=', fields.Date.to_string(date.today())),
        ]).action_start_contract()

        contract_ids = self.search([('date_end', '=', False), ('state', '=', 'close'), ('employee_id', '!=', False)])
        # Ensure all closed contract followed by a new contract have a end date.
        # If closed contract has no closed date, the work entries will be generated for an unlimited period.
        for contract in contract_ids:
            next_contract = self.search([
                ('employee_id', '=', contract.employee_id.id),
                ('state', 'not in', ['cancel', 'new']),
                ('date_start', '>', contract.date_start)
            ], order="date_start asc", limit=1)
            if next_contract:
                contract.date_end = next_contract.date_start - relativedelta(days=1)
                continue
            next_contract = self.search([
                ('employee_id', '=', contract.employee_id.id),
                ('date_start', '>', contract.date_start)
            ], order="date_start asc", limit=1)
            if next_contract:
                contract.date_end = next_contract.date_start - relativedelta(days=1)

        return True

    def action_start_contract(self):
        """
        Set to Running status
        """
        for r in self:
            if r.state != 'draft':
                raise UserError(_("You may not be able to start the contract %s while its status is not New") % (r.name,))
        return self.with_context(action_call=True).write({'state': 'open'})

    def action_to_renew(self):
        """
        Set to 'To Renew' status
        """
        for r in self:
            if r.state != 'open':
                raise UserError(_("You may not be able to set the contract %s as To Renew while its status is not Running") % (r.name,))
        return self.with_context(action_call=True).write({'kanban_state': 'blocked'})

    def action_renew(self):
        """
        Set to Running status
        """
        for r in self:
            if r.state != 'close':
                raise UserError(_("You may not be able to renew the contract %s while its status is neither To Renew nor Expired") % (r.name,))
        return self.with_context(action_call=True).write({'state': 'open'})

    def set_as_close(self):
        """
        Set to Expired status
        """
        for r in self:
            if r.state != 'open':
                raise UserError(_("You may not be able to set expired the contract %s while its status is neither Running nor To Renew") % (r.name,))
        return self.with_context(action_call=True).write({'state': 'close'})

    def action_cancel(self):
        """
        Set to Cancel status
        """
        for r in self:
            if r.state not in ('close', 'open'):
                raise UserError(_("You may not be able to cancel the contract %s while its status is neither Running nor To Renew nor Expired.")
                                % (r.name,))
        return self.with_context(action_call=True).write({'state': 'cancel'})

    def action_set_to_draft(self):
        """
        Set to Draft status
        """
        for r in self:
            if r.state != 'cancel':
                raise UserError(_("You may not be able to set to draft the contract %s while its status is not Cancelled") % (r.name,))
        return self.with_context(action_call=True).write({'state': 'draft'})

    def write(self, vals):
        if 'state' in vals and not self._context.get('action_call', False):
            state_change = self.filtered(lambda c: c.state != vals['state'])
            if vals['state'] == 'draft':
                state_change.action_set_to_draft()
            elif vals['state'] == 'cancel':
                state_change.action_cancel()
            elif vals['state'] == 'close':
                state_change.set_as_close()
            elif vals['state'] == 'open':
                draft_contract_ids = state_change.filtered(lambda r: r.state == 'draft')
                draft_contract_ids.action_start_contract()
                (state_change - draft_contract_ids).action_renew()
            else:
                raise ValidationError(_("Invalid status %s") % (vals['state'],))
            del(vals['state'])
        return super(HrContract, self).write(vals)

