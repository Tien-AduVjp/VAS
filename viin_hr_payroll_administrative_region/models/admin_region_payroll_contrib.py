from odoo import models, fields


class AdministrativeRegionPayrollContribution(models.Model):
    _name = 'admin.region.payroll.contrib'
    _description = 'Administrative Region Payroll Contribution'
    _inherit = 'mail.thread'

    administrative_region_id = fields.Many2one('administrative.region', string='Administrative Region', required=True, tracking=True)
    payroll_contribution_type_id = fields.Many2one('hr.payroll.contribution.type', string='Payroll Contribution Type', required=True, tracking=True)
    company_id = fields.Many2one(related='payroll_contribution_type_id.company_id', store=True)
    country_id = fields.Many2one(related='administrative_region_id.country_id', store=True)
    currency_id = fields.Many2one(related='company_id.currency_id', store=True)
    max_contribution_base = fields.Monetary(string="Max. Contribution Base", default=0.0, required=True, tracking=True,
                                  help="The amount that is used to bound the maximum base for payroll contribution of the combination of the type and the administrative region specified here. \
                                  Leave it zero to disable this bound.")
    min_contribution_base = fields.Monetary(string="Min. Contribution Base", default=0.0, required=True, tracking=True,
                                  help="The amount that is used to bound the minimum base for payroll contribution of the combination of the type and the administrative region specified here. \
                                  Leave it zero to disable this bound.")

    max_contribution_employee = fields.Monetary(string="Max. Contribution by Employee", default=0.0, tracking=True,
                                  help="The maximum amount per month that the employee has to contribute. Leave this zero to disable this limit.")
    max_contribution_company = fields.Monetary(string="Max. Contribution by Company", default=0.0, tracking=True,
                                  help="The maximum amount per month that the company has to contribute. Leave this zero to disable this limit.")

    _sql_constraints = [
        ('check_unique',
         "UNIQUE(administrative_region_id,payroll_contribution_type_id)",
         "Administrative Region Payroll Contribution must be unique per Administrative Region & Payroll Contribution Type."),
        ('check_contrib_base',
         "CHECK(max_contribution_base >= min_contribution_base)",
         "Max. Contribution Base must be greater than or equal Min. Contribution Base!"),
        ('check_min_contrib_base_emp',
         "CHECK(min_contribution_base >= 0)",
         "Min. Contribution Base must be greater than or equal 0!"),
        ('check_max_contrib_emp',
         "CHECK(max_contribution_employee >= 0)",
         "Max. Contribution by Employee must be greater than or equal 0!"),
        ('check_max_contrib_comp',
         "CHECK(max_contribution_company >= 0)",
         "Max. Contribution by Company must be greater than or equal 0!")
    ]

    def name_get(self):
        return self.mapped(lambda r: (r.id, "[%s] %s" %(r.administrative_region_id.name, r.payroll_contribution_type_id.name)))

    def _qualify_contribution_base(self, contribution_base):
        """
        Ensure the given contribution base is within the allowed min/max contribution bound by the administrative region
        for the corresponding contribution type
        """
        self.ensure_one()
        if self.min_contribution_base > 0.0 and contribution_base < self.min_contribution_base:
            contribution_base = self.min_contribution_base
        if self.max_contribution_base > 0.0 and contribution_base > self.max_contribution_base:
            contribution_base = self.max_contribution_base
        return contribution_base
