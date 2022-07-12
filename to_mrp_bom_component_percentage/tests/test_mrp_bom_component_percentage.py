from odoo.tests.common import tagged
from odoo.exceptions import ValidationError
from odoo.addons.mrp.tests.common import TestMrpCommon


@tagged('post_install', '-at_install')
class TestBoMComponentPercentage(TestMrpCommon):
    
    @classmethod
    def setUpClass(cls):
        super(TestBoMComponentPercentage, cls).setUpClass()
    
    def test_01_constrains_with_all_positive_percentages(self):
        self.assertEqual(len(self.bom_1.bom_line_ids), 2, "Error testing: This bom_1 is expected to have 2 BoM lines.")
        
        bom_line_ids = self.bom_1.bom_line_ids.ids
        self.bom_1.write({
            'bom_line_ids': [
                (1, bom_line_ids[0], {'price_percent': 55.5}),
                (1, bom_line_ids[1], {'price_percent': 44.5})
            ]
        })
        
        total_percentage = sum(self.bom_1.bom_line_ids.mapped('price_percent'))
        self.assertEqual(total_percentage, 100, "Error testing: The total percentage of this BoM should be 100.")
        
    def test_02_constrains_with_negative_percentages(self):
        self.assertEqual(len(self.bom_1.bom_line_ids), 2, "Error testing: This bom_1 is expected to have 2 BoM lines.")
        with self.assertRaises(ValidationError):
            self.bom_1.write({
                'bom_line_ids': [(1, bom_line.id, {'price_percent':-50}) for bom_line in self.bom_1.bom_line_ids]
            })
            
    def test_03_constrains_with_percentages_are_decimal(self):
        self.assertEqual(len(self.bom_1.bom_line_ids), 2, "Error testing: This bom_1 is expected to have 2 BoM lines.")
        with self.assertRaises(ValidationError):
            self.bom_1.write({
                'bom_line_ids': [(1, bom_line.id, {'price_percent': 0.01}) for bom_line in self.bom_1.bom_line_ids]
            })
            
    def test_04_constrains_with_sum_percentages_between_0_and_100(self):
        self.assertEqual(len(self.bom_1.bom_line_ids), 2, "Error testing: This bom_1 is expected to have 2 BoM lines.")
        with self.assertRaises(ValidationError):
            self.bom_1.write({
                'bom_line_ids': [(1, bom_line.id, {'price_percent': 1}) for bom_line in self.bom_1.bom_line_ids]
            })

    def test_05_constrains_with_sum_of_all_percentage(self):
        self.assertEqual(len(self.bom_1.bom_line_ids), 2, "Error testing: This bom_1 is expected to have 2 BoM lines.")
        # Test case the sum > 100%
        with self.assertRaises(ValidationError):
            self.bom_1.write({
                'bom_line_ids': [(1, bom_line.id, {'price_percent': 99}) for bom_line in self.bom_1.bom_line_ids]
            })
    
    def test_06_constrains_sum_percentage_is_zero(self):
        self.assertEqual(len(self.bom_1.bom_line_ids), 2, "Error testing: This bom_1 is expected to have 2 BoM lines.")
        # Accept sum of all percentages = 0
        self.bom_1.write({
            'bom_line_ids': [(1, bom_line.id, {'price_percent': 0}) for bom_line in self.bom_1.bom_line_ids]
        })
    
    def test_07_constains_any_line_has_zero_percentage(self):
        self.assertEqual(len(self.bom_1.bom_line_ids), 2, "Error testing: This bom_1 is expected to have 2 BoM lines.")
    
        bom_line_ids = self.bom_1.bom_line_ids.ids
        with self.assertRaises(ValidationError):
            self.bom_1.write({
                    'bom_line_ids': [
                        (1, bom_line_ids[0], {'price_percent': 100}),
                        (1, bom_line_ids[1], {'price_percent': 0}),
                    ]
                })
