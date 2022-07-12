from odoo.tests.common import tagged
from odoo.tests import SavepointCase


@tagged('post_install', '-at_install')
class TestAdministrativeRegion(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestAdministrativeRegion, cls).setUpClass()

        company = cls.env['res.company'].create({
            'name': 'New company',
            'country_id': cls.env.ref('base.vn').id
        })

        cls.region_1 = cls.env.ref('viin_administrative_region.administrative_region_1')
        cls.region_2 = cls.env.ref('viin_administrative_region.administrative_region_2')
        cls.region_3 = cls.env.ref('viin_administrative_region.administrative_region_3')
        cls.region_4 = cls.env.ref('viin_administrative_region.administrative_region_4')

        PayrollContribType = cls.env['hr.payroll.contribution.type']
        cls.social_insurance = PayrollContribType.search([('code', '=', 'SOCIAL_INSURANCE'), ('company_id', '=', company.id)])
        cls.heath_insurance = PayrollContribType.search([('code', '=', 'HEALTH_INSURANCE'), ('company_id', '=', company.id)])
        cls.unemployment_unsurance = PayrollContribType.search([('code', '=', 'UNEMPLOYMENT_UNSURANCE'), ('company_id', '=', company.id)])
        cls.labor_union = PayrollContribType.search([('code', '=', 'LABOR_UNION'), ('company_id', '=', company.id)])

    def test_minimum_wage(self):
        self.assertEqual(self.region_1.minimum_wage, 4420000)
        self.assertEqual(self.region_2.minimum_wage, 3920000)
        self.assertEqual(self.region_3.minimum_wage, 3430000)
        self.assertEqual(self.region_4.minimum_wage, 3070000)

    def test_contribution_social_insurance(self):
        contrib_social_insurances = self.env['admin.region.payroll.contrib'].search([('payroll_contribution_type_id', '=', self.social_insurance.id)])
        self.assertRecordValues(
            contrib_social_insurances,
            [{
                'min_contribution_base': 4420000,
                'max_contribution_base': 29800000,
                'max_contribution_employee': 0,
                'max_contribution_company': 0
            },
            {
                'min_contribution_base': 3920000,
                'max_contribution_base': 29800000,
                'max_contribution_employee': 0,
                'max_contribution_company': 0
            },
            {
                'min_contribution_base': 3430000,
                'max_contribution_base': 29800000,
                'max_contribution_employee': 0,
                'max_contribution_company': 0
            },
            {
                'min_contribution_base': 3070000,
                'max_contribution_base': 29800000,
                'max_contribution_employee': 0,
                'max_contribution_company': 0
            }])

    def test_contribution_heath_insurance(self):
        contrib_heath_insurances = self.env['admin.region.payroll.contrib'].search([('payroll_contribution_type_id', '=', self.heath_insurance.id)])
        self.assertRecordValues(
            contrib_heath_insurances,
            [{
                'min_contribution_base': 4420000,
                'max_contribution_base': 29800000,
                'max_contribution_employee': 0,
                'max_contribution_company': 0
            },
            {
                'min_contribution_base': 3920000,
                'max_contribution_base': 29800000,
                'max_contribution_employee': 0,
                'max_contribution_company': 0
            },
            {
                'min_contribution_base': 3430000,
                'max_contribution_base': 29800000,
                'max_contribution_employee': 0,
                'max_contribution_company': 0
            },
            {
                'min_contribution_base': 3070000,
                'max_contribution_base': 29800000,
                'max_contribution_employee': 0,
                'max_contribution_company': 0
            }])

    def test_contribution_unemployment_unsurance(self):
        contrib_unemployment_unsurances = self.env['admin.region.payroll.contrib'].search([('payroll_contribution_type_id', '=', self.unemployment_unsurance.id)])
        self.assertRecordValues(
            contrib_unemployment_unsurances,
            [{
                'min_contribution_base': 4420000,
                'max_contribution_base': 88400000,
                'max_contribution_employee': 0,
                'max_contribution_company': 0
            },
            {
                'min_contribution_base': 3920000,
                'max_contribution_base': 78400000,
                'max_contribution_employee': 0,
                'max_contribution_company': 0
            },
            {
                'min_contribution_base': 3430000,
                'max_contribution_base': 68600000,
                'max_contribution_employee': 0,
                'max_contribution_company': 0
            },
            {
                'min_contribution_base': 3070000,
                'max_contribution_base': 61400000,
                'max_contribution_employee': 0,
                'max_contribution_company': 0
            }])

    def test_contribution_labor_union(self):
        contrib_labor_unions = self.env['admin.region.payroll.contrib'].search([('payroll_contribution_type_id', '=', self.labor_union.id)])
        self.assertRecordValues(
            contrib_labor_unions,
            [{
                'min_contribution_base': 4420000,
                'max_contribution_base': 29800000,
                'max_contribution_employee': 149000,
                'max_contribution_company': 0
            },
            {
                'min_contribution_base': 3920000,
                'max_contribution_base': 29800000,
                'max_contribution_employee': 149000,
                'max_contribution_company': 0
            },
            {
                'min_contribution_base': 3430000,
                'max_contribution_base': 29800000,
                'max_contribution_employee': 149000,
                'max_contribution_company': 0
            },
            {
                'min_contribution_base': 3070000,
                'max_contribution_base': 29800000,
                'max_contribution_employee': 149000,
                'max_contribution_company': 0
            }])
