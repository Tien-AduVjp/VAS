from odoo import models


class ResCompany(models.Model):
    _inherit = 'res.company'

    def _generate_salary_structures(self):
        res = super(ResCompany, self)._generate_salary_structures()
        self._generate_admin_region_payroll_contrib()
        return res

    def _generate_admin_region_payroll_contrib(self):
        """
        Hooking method for others module to generate localized `admin.region.payroll.contrib` records
        """
        return self.env['admin.region.payroll.contrib']
