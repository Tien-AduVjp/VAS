from psycopg2 import IntegrityError
from odoo.tools import mute_logger
from odoo.tests import SavepointCase, tagged


@tagged('post_install', '-at_install')
class TestAdministrativeRegionPayrollContribution(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestAdministrativeRegionPayrollContribution, cls).setUpClass()
        cls.contribution_type = cls.env['hr.payroll.contribution.type'].search([('company_id', '=', cls.env.company.id)], limit=1)
        cls.RegionContribution = cls.env['admin.region.payroll.contrib'].with_context(tracking_disable=True)

    def test_create_record(self):
        record = self.RegionContribution.create({
            'administrative_region_id': self.env.ref('viin_administrative_region.administrative_region_1').id,
            'payroll_contribution_type_id': self.contribution_type.id,
            'min_contribution_base': 1000,
            'max_contribution_base': 5000,
            'max_contribution_employee': 200,
            'max_contribution_company':200
        })
        self.assertTrue(record)

    def test_sql_contraint_0(self):
        """
        Check Unique: administrative_region_id, payroll_contribution_type_id
        """
        self.RegionContribution.create({
            'administrative_region_id': self.env.ref('viin_administrative_region.administrative_region_1').id,
            'payroll_contribution_type_id': self.contribution_type.id,
            'min_contribution_base': 1000,
            'max_contribution_base': 5000
        })
        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'):
            self.RegionContribution.create({
                'administrative_region_id': self.env.ref('viin_administrative_region.administrative_region_1').id,
                'payroll_contribution_type_id': self.contribution_type.id,
                'min_contribution_base': 2000,
                'max_contribution_base': 10000
            })

    def test_sql_contraint_1(self):
        """
        Max. Contribution Base must be greater than or equal Min. Contribution Base
        """
        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'):
            self.RegionContribution.create({
                'administrative_region_id': self.env.ref('viin_administrative_region.administrative_region_1').id,
                'payroll_contribution_type_id': self.contribution_type.id,
                'min_contribution_base': 1000,
                'max_contribution_base': 500,
                'max_contribution_employee': 200,
                'max_contribution_company':200
            })

    def test_sql_contraint_2(self):
        """
        Min. Contribution Base must be greater than or equal 0
        """
        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'):
            self.RegionContribution.create({
                'administrative_region_id': self.env.ref('viin_administrative_region.administrative_region_1').id,
                'payroll_contribution_type_id': self.contribution_type.id,
                'min_contribution_base': -1000,
                'max_contribution_base': -500,
                'max_contribution_employee': 200,
                'max_contribution_company':200
            })

    def test_sql_contraint_3(self):
        """
        Max. Contribution by Employee must be greater than or equal 0
        """
        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'):
            self.RegionContribution.create({
                'administrative_region_id': self.env.ref('viin_administrative_region.administrative_region_1').id,
                'payroll_contribution_type_id': self.contribution_type.id,
                'min_contribution_base': 1000,
                'max_contribution_base': 5000,
                'max_contribution_employee': -100,
                'max_contribution_company':200
            })

    def test_sql_contraint_4(self):
        """
        Max. Contribution by Company must be greater than or equal 0
        """
        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'):
            self.RegionContribution.create({
                'administrative_region_id': self.env.ref('viin_administrative_region.administrative_region_1').id,
                'payroll_contribution_type_id': self.contribution_type.id,
                'min_contribution_base': 1000,
                'max_contribution_base': 5000,
                'max_contribution_employee': 100,
                'max_contribution_company': -200
            })
