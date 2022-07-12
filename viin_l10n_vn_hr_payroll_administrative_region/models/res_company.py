from odoo import models


class ResCompany(models.Model):
    _inherit = 'res.company'

    def write(self, vals):
        set_payroll_contrib_data = 'country_id' in vals
        res = super(ResCompany, self).write(vals)
        if set_payroll_contrib_data:
            self._l10n_vn_generate_admin_region_payroll_contrib()
        return res

    def _generate_admin_region_payroll_contrib(self):
        records = super(ResCompany, self)._generate_admin_region_payroll_contrib()
        vietnam_companies = self.filtered(lambda comp: comp.country_id == self.env.ref('base.vn'))
        if vietnam_companies:
            records |= vietnam_companies._l10n_vn_generate_admin_region_payroll_contrib()
        return records

    def _l10n_vn_generate_admin_region_payroll_contrib(self):
        """
        Reference Links:
        https://luatvietnam.vn/bao-hiem/muc-dong-bhxh-2021-563-27501-article.html
        http://ketoanthienung.vn/doan-phi-cong-doan-va-kinh-phi-cong-doan.htm
        """
        vietnam = self.env.ref('base.vn')
        companies = self.filtered(lambda r: r.partner_id.country_id == vietnam)
        contribution_types = self.env['hr.payroll.contribution.type'].sudo().search([('company_id', 'in', companies.ids)])
        regions = self.env['administrative.region'].search([('country_id', '=', vietnam.id)])
        vals_list = []
        for contribution_type in contribution_types:
            for region in regions:
                if self.env['admin.region.payroll.contrib'].sudo().search([
                    ('administrative_region_id', '=', region.id),
                    ('payroll_contribution_type_id', '=', contribution_type.id)
                    ]):
                    continue
                vals = {
                    'administrative_region_id': region.id,
                    'payroll_contribution_type_id': contribution_type.id,
                    'min_contribution_base': region.minimum_wage,
                    'max_contribution_base': 29800000
                }
                if contribution_type.code == 'UNEMPLOYMENT_UNSURANCE':
                    vals['max_contribution_base'] = 20 * region.minimum_wage
                elif contribution_type.code == 'LABOR_UNION':
                    vals['max_contribution_employee'] = 149000
                vals_list.append(vals)
        if vals_list:
            return self.env['admin.region.payroll.contrib'].sudo().create(vals_list)
        return self.env['admin.region.payroll.contrib']
