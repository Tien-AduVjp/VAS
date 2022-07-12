from odoo import fields, models, api


class HrContract(models.Model):
    _inherit = 'hr.contract'
    
    administrative_region_id = fields.Many2one('administrative.region', string='Administrative Region', tracking=True,
                                               compute="_compute_administrative_region_id", store=True, readonly=False)
    admin_region_payroll_contrib_ids = fields.Many2many('admin.region.payroll.contrib', string='Administrative Region Payroll Contributions',
                                                        compute='_compute_admin_region_payroll_contrib_ids')
    
    @api.depends('employee_id')
    def _compute_administrative_region_id(self):
        for r in self:
            if r.employee_id.administrative_region_id:
                r.administrative_region_id = r.employee_id.administrative_region_id
            else: 
                r.administrative_region_id = False

    @api.depends('administrative_region_id', 'payroll_contribution_type_ids')
    def _compute_admin_region_payroll_contrib_ids(self):
        admin_region_payroll_contribs = self.env['admin.region.payroll.contrib'].search(self._get_admin_region_payroll_contrib_domain())
        for r in self:
            contribs = admin_region_payroll_contribs.filtered(
                lambda contrib: contrib.administrative_region_id == r.administrative_region_id \
                and contrib.payroll_contribution_type_id.id in r.payroll_contribution_type_ids.ids
                )
            r.admin_region_payroll_contrib_ids = [(6, 0, contribs.ids)]
    
    def _assign_open_contract(self):
        super(HrContract, self)._assign_open_contract()
        for contract in self:
            contract.employee_id.sudo().write({'administrative_region_id': contract.administrative_region_id.id})
    
    def _get_admin_region_payroll_contrib_domain(self):
        return [
            ('administrative_region_id', 'in', self.administrative_region_id.ids),
            ('payroll_contribution_type_id', 'in', self.payroll_contribution_type_ids.ids)
            ]
