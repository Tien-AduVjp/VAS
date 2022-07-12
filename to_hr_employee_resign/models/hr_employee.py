from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    hr_employee_resignation_ids = fields.One2many('hr.employee.resignation', 'employee_id', string='Resignations')
    hr_employee_resignations_count = fields.Integer(string='Resignations Count',
                                                    compute='_compute_hr_employee_resignations_count',
                                                    store=True, groups='hr.group_hr_user')
    resigned = fields.Boolean(string='Resigned', compute='_compute_resigned', store=True, groups='hr.group_hr_user')

    @api.depends('hr_employee_resignation_ids')
    def _compute_hr_employee_resignations_count(self):
        for r in self:
            r.hr_employee_resignations_count = len(r.hr_employee_resignation_ids)

    def action_view_resignations(self):
        action = self.env['ir.actions.act_window']._for_xml_id('to_hr_employee_resign.hr_employee_resignation_action')

        # override the context to get rid of the default filtering
        action['context'] = {'employee_id': self.id, 'default_employee_id': self.id}

        # choose the view_mode accordingly
        if len(self.hr_employee_resignation_ids) != 1:
            action['domain'] = "[('id', 'in', " + str(self.hr_employee_resignation_ids.ids) + ")]"
        elif len(self.hr_employee_resignation_ids) == 1:
            res = self.env.ref('to_hr_employee_resign.hr_employee_resignation_form', False)
            action['views'] = [(res and res.id or False, 'form')]
            action['res_id'] = self.hr_employee_resignation_ids.id
        return action

    @api.depends('hr_employee_resignation_ids', 'contract_ids', 'contract_ids.state')
    def _compute_resigned(self):
        for r in self:
            if r.hr_employee_resignation_ids and r.contract_ids and all(contract.state not in ('draft', 'open', 'pending') for contract in r.contract_ids):
                r.resigned = True
            else:
                r.resigned = False
