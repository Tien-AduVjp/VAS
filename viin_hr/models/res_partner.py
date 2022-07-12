from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # 'employee' is a field of 'base' module but does not display on any view or use in anywhere,
    # so I make use for it here
    employee = fields.Boolean(compute='_compute_is_employee', store=True, groups='hr.group_hr_user')
    tmp_employee_ids = fields.One2many('hr.employee', 'address_home_id', string='Temporary Employees', groups='hr.group_hr_user',
                                        help="Technical field that stores the employees using this partner as its private address.")
    employee_ids = fields.Many2many('hr.employee', 'viin_res_partner_employee_rel', 'partner_id', 'employee_id',
                                    string='Related Employees', compute='_compute_employee_ids', store=True,
                                    groups="hr.group_hr_user")

    @api.depends('user_ids.employee_ids', 'tmp_employee_ids')
    def _compute_employee_ids(self):
        all_employees = self.env['hr.employee'].with_context(active_test=False).search_read(
            ['|', ('address_home_id', 'in', self.ids), ('user_id.partner_id', 'in', self.ids)],
            ['address_home_id', 'user_id'])
        # prefetching partner's user_ids for performance later in loop
        if self.ids:
            self.read(['user_ids'])
        for r in self:
            employees = filter(
                lambda emp: \
                (emp['address_home_id'] and emp['address_home_id'][0] == r.id) \
                or (emp['user_id'] and emp['user_id'][0] in r.user_ids.ids),
                all_employees
                )
            r.employee_ids = [(6, 0, [emp['id'] for emp in employees])]

    @api.depends('employee_ids')
    def _compute_is_employee(self):
        for r in self:
            r.employee = bool(r.employee_ids)

    def _get_hr_allowed_fields(self):
        return self._address_fields() + ['phone', 'mobile', 'email', 'dob', 'bank_ids', 'name', 'company_id', 'type']

    def write(self, vals):
        """
        Dirty hack to allow HR officer to update employee's private address without res.users access rights error
        """
        if self.env.user.has_group('hr.group_hr_user') and all(f in self._get_hr_allowed_fields() for f in vals.keys()):
            return super(ResPartner, self.with_context(group_hr_user_update_private_address=True)).write(vals)
        return super(ResPartner, self).write(vals)
