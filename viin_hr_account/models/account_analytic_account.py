from odoo import fields, models, api, _
from odoo.exceptions import UserError


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    department_ids = fields.One2many('hr.department', 'analytic_account_id', string='HR Departments',
                                         help="Technical field to link analytic account to HR departments.")

    department_id = fields.Many2one('hr.department', string='HR Department',
                                       compute='_compute_department_id',
                                       store=True, tracking=True)

    def write(self, vals):
        if 'name' in vals and not self.env.context.get('force_write', False):
            for r in self.filtered(lambda acc: acc.department_id):
                raise UserError(_("You may not be able to change the name of the account '%s'"
                                  " while it links to the HR department '%s'")
                                  % (r.display_name, r.department_id.display_name))
        return super(AccountAnalyticAccount, self).write(vals)

    @api.constrains('department_ids')
    def _check_department_ids(self):
        for r in self:
            if len(r.department_ids) > 1:
                raise UserError(_("You may not have a single analytic account that links to multiple HR departments."))

    @api.depends('department_ids')
    def _compute_department_id(self):
        for r in self:
            r.department_id = r.department_ids[0] if r.department_ids else False

    def _prepare_analytic_distribution_line_vals(self, percentage=100.0):
        self.ensure_one()
        return {
            'name': self.name,
            'account_id': self.id,
            'percentage': percentage
            }
