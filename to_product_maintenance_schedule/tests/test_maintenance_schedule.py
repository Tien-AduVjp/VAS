from psycopg2 import IntegrityError, InternalError

try:
    from psycopg2.errors import InFailedSqlTransaction
except:
    InFailedSqlTransaction = IntegrityError

from odoo import tools
from odoo.tests import tagged
from odoo.exceptions import ValidationError

from .common import MaintenanceScheduleCommon


@tagged('post_install', '-at_install')
class TestMaintenanceSchedule(MaintenanceScheduleCommon):

    def test_10_sql_constraints(self):
        """Test case 5"""
        # an InternalError (ROLLBACK should work, maybe).
        try:
            with tools.mute_logger('odoo.sql_db'):
                with self.assertRaises(IntegrityError):
                    self.env['maintenance.action'].create({
                        'name': 'test_action',
                        'service_id': self.product.id,
                        'part_replacement': False,
                        })
                with self.assertRaises(InFailedSqlTransaction):
                    self.env['maintenance.schedule'].create({
                        'part': 'test_part',
                        'product_milestone_id': self.milestone.id,
                        'maintenance_action_id': self.action.id,
                        })
        except InternalError:
            pass

    def test_11_check_product_id(self):
        """Test case 6"""
        self.schedule._check_product_id()
        self.action.write({'part_replacement': True})
        self.assertRaises(ValidationError, self.schedule._check_product_id)
