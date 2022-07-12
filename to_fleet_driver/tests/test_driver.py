from datetime import datetime, timedelta

from odoo import _
from odoo.exceptions import UserError
from odoo.tests.common import tagged, TransactionCase


@tagged('post_install', '-at_install')
class TestDriver(TransactionCase):
    
    def setUp(self):
        super(TestDriver, self).setUp()
        
        ResPartner = self.env['res.partner']
        self.driver_with_license = ResPartner.create({'name': 'driver1'})
        self.driver_without_license = ResPartner.create({'name': 'driver2'})

        self.license = self.env['fleet.driver.license'].create({
                'legal_number': '001',
                'driver_id': self.driver_with_license.id,
                'expired_date': datetime.today() + timedelta(days=1),
                'state': 'confirmed'
            })
        
        model_vehicle = self.env.ref('fleet.brand_audi')
        
        self.vehicle = self.env['fleet.vehicle'].create({
                'model_id': model_vehicle.id
            })
        
    def _apply_cron(self):
        self.env.ref('to_fleet_driver.ir_cron_find_and_set_driver_licenses_expired').method_direct_trigger()
    
    def test_compute_days_left(self):
        """
        This test ensures days_left value compute exactly
        """
        self.assertEqual(self.license.days_left, 1, "compute days_left wrong")
        
        self.license.expired_date = datetime.today() - timedelta(days=1)
        self.assertEqual(self.license.days_left, -1, "compute days_left wrong")

        self.license.expired_date = False
        self.assertEqual(self.license.days_left, 100000, "compute days_left wrong")

    def test_cron_find_and_set_expire_license(self):
        """
        This test ensures cron changing state value of license will compute exactly
        """
        self._apply_cron()
        self.assertNotEqual(self.license.state, 'expired', "Cron set expire wrong!")
        
        self.license.state = 'confirmed' 
        self.license.expired_date = datetime.today()
        self._apply_cron()
        self.assertEqual(self.license.state, 'expired', "Cron set expire not work!")

        self.license.state = 'confirmed' 
        self.license.expired_date = datetime.today() - timedelta(days=1)
        self._apply_cron()
        self.assertEqual(self.license.state, 'expired', "Cron set expire not work!")
        
        # check cron run multi records
        self.license.state = 'confirmed'
        self.env['fleet.driver.license'].create({
                'legal_number': '002',
                'driver_id': self.driver_without_license.id,
                'expired_date': datetime.today() - timedelta(days=1),
                'state': 'confirmed'
            })
        self._apply_cron()

    def test_driver_license_duplication(self):
        copied_license1 = self.license.copy()
        self.assertRecordValues(
            copied_license1,
            [
                {
                    'legal_number': _("%s (copy)") % '001',
                    'driver_id': self.driver_with_license.id,
                    'state': 'draft'
                    }
                ]
            )
        self.assertRecordValues(
            copied_license1.copy(),
            [
                {
                    'legal_number': _("%s (copy)") % _("%s (copy)") % '001',
                    'driver_id': self.driver_with_license.id,
                    'state': 'draft'
                    }
                ]
            )

    def test_driver_license_number_duplication(self):
        copied_license = self.license.copy()
        with self.assertRaises(UserError):
            copied_license.write({'legal_number': '001'})
        with self.assertRaises(UserError):
            self.license = self.env['fleet.driver.license'].create({
                'legal_number': '001',
                'driver_id': self.driver_with_license.id,
                'expired_date': datetime.today() + timedelta(days=1),
                'state': 'confirmed'
            })
        
