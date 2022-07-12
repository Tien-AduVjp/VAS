import psycopg2
try:
    from psycopg2 import errors
    UniqueViolation = errors.UniqueViolation
except Exception:
    UniqueViolation = psycopg2.IntegrityError
from odoo.tools import mute_logger
from odoo.tests.common import tagged, Form
from odoo.exceptions import ValidationError, UserError
from .common import Common


@tagged('-at_install', 'post_install')
class Quality(Common):

    def test_01_validate_qty_deviation(self):
        """
        Case 6: Verify checked quantity deviation when quality check
        """
        self.quality_check = self.env['quality.check'].with_context(tracking_disable=True).create({
            'point_id': self.quality_point_measure.id,
            'product_id': self.quality_point_measure.product_id.id,
            'team_id': self.quality_point_measure.team_id.id,
            'checked_quantity': 80.00
        })
        self.quality_check.do_pass()
        self.assertEqual(self.quality_check.checked_qty_deviation, -20.00)

    def test_11_validate_product(self):
        """
        Case 7: Verify when creating quality check there is a different product from the quality point product
        """
        with self.assertRaises(ValidationError):
            self.quality_check = self.env['quality.check'].with_context(tracking_disable=True).create({
                'point_id': self.quality_point_measure.id,
                'product_id': self.product_c.id,
                'team_id': self.quality_point_measure.team_id.id,
                'checked_quantity': 80.00
            })

    def test_12_validate_product(self):
        """
        Case 8: Validate when creating a quality check that the product is the same as the product variant of the quality point product
        """
        self.quality_point_measure.product_id = False
        self.quality_check = self.env['quality.check'].with_context(tracking_disable=True).create({
            'point_id': self.quality_point_measure.id,
            'product_id': self.product_a2.id,
            'team_id': self.quality_point_measure.team_id.id,
            'checked_quantity': 80.00
        })
        self.assertEqual(len(self.quality_check), 1)

    def test_21_delete_quality_point(self):
        """
        Case 3: Quality point cannot be deleted once a quality check has been created with it
        """
        self.quality_check = self.env['quality.check'].with_context(tracking_disable=True).create({
            'point_id': self.quality_point_measure.id,
            'product_id': self.quality_point_measure.product_id.id,
            'team_id': self.quality_point_measure.team_id.id,
            'checked_quantity': 80.00
        })
        with self.assertRaises(UserError):
            self.quality_point_measure.unlink()

    def test_31_action_name_unique(self):
        """
        Case 4: Check for duplication of quality actions
        """
        self.quality_action = self.env['quality.action'].with_context(tracking_disable=True).create({
            'name': 'Action 1',
        })
        with self.assertRaises(psycopg2.IntegrityError), mute_logger('odoo.sql_db'):
            self.quality_action = self.env['quality.action'].with_context(tracking_disable=True).create({
                'name': 'Action 1',
            })
