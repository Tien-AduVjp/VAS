from lxml import html

from odoo import fields
from odoo.tests import tagged

from .test_base import TestBase


@tagged('post_install', '-at_install')
class TestProductionLot(TestBase):
    
    def test_after_install_module_01(self):
        """
        [Functional Test] - TC01
        
        - Case: Check new paper format is created after install module
        - Expected Result: New paper format with format is A4 and orientation is Landscape is created
        """
        new_paper_format = self.env.ref('to_repair_extend.to_repair_report_landscape')
        self.assertTrue(new_paper_format.name == 'Repair Report')
        self.assertTrue(new_paper_format.format == 'A4')
        self.assertTrue(new_paper_format.orientation == 'Landscape')
    
    
    def _validate_repair_report_values(self, expected_values_list):
        reports = self.env['repair.report'].read_group(domain=[('company_id', '=', self.company.id)], 
                                                       fields=['operation_product_id', 'repair_product_id', 
                                                        'operation_product_uom_qty','price_subtotal'],
                                                       groupby=['id','operation_product_id', 'repair_product_id'], 
                                                       orderby='operation_product_id, repair_product_id asc',
                                                       lazy=False)
        report_values_dict = [{
            'operation_product_id': vals.get('operation_product_id')[0],
            'repair_product_id': vals.get('repair_product_id')[0],
            'operation_product_uom_qty': vals.get('operation_product_uom_qty'),
            'price_subtotal': vals.get('price_subtotal'),
        } for vals in reports]
        
        expected_values_dict = [{
            'operation_product_id': vals[0],
            'repair_product_id': vals[1],
            'operation_product_uom_qty': vals[2],
            'price_subtotal': vals[3],
        } for vals in expected_values_list]
        
        self.assertTrue(len(report_values_dict) == len(expected_values_dict))
        
        for report, expected in zip(report_values_dict, expected_values_dict):
            self.assertDictEqual(report, expected)
    
    def test_repair_report_on_new_pivot_01(self):
        """
        [Functional Test] - TC04
        
        - Case: Check data of repair report on new pivot
        - Expected Result: Data of repair report on pivot is correct with created data in database
        """
        expected_values_list = [
            # operation_product_id        repair_product_id             operation_product_uom_qty    price_subtotal
            [self.product_consu1.id,       self.product_to_repair1.id,          1.0,                        100.0],
            [self.product_consu1.id,       self.product_to_repair1.id,          1.0,                        100.0],
            [self.product_consu2.id,       self.product_to_repair2.id,          1.0,                        150.0],
            [self.product_consu3.id,       self.product_to_repair3.id,          1.0,                        100.0],
            [self.product_consu4.id,       self.product_to_repair4.id,          1.0,                        120.0],
            [self.product_consu5.id,       self.product_to_repair5.id,          1.0,                        250.0],
            [self.product_product1.id,     self.product_to_repair1.id,          1.0,                        200.0],
            [self.product_product1.id,     self.product_to_repair1.id,          1.0,                        200.0],
            [self.product_product2.id,     self.product_to_repair2.id,          1.0,                        200.0],
            [self.product_product3.id,     self.product_to_repair3.id,          1.0,                        200.0],
            [self.product_product4.id,     self.product_to_repair4.id,          1.0,                        230.0],
            [self.product_product5.id,     self.product_to_repair5.id,          1.0,                        150.0],
            [self.product_service1.id,     self.product_to_repair1.id,          1.0,                        150.0],
            [self.product_service1.id,     self.product_to_repair1.id,          1.0,                        150.0],
            [self.product_service1.id,     self.product_to_repair4.id,          1.0,                        150.0],
            [self.product_service2.id,     self.product_to_repair2.id,          1.0,                        200.0],
            [self.product_service2.id,     self.product_to_repair5.id,          1.0,                        200.0],
            [self.product_service3.id,     self.product_to_repair3.id,          1.0,                        250.0],
        ]
        self._validate_repair_report_values(expected_values_list)
        
        
    def test_render_report_01(self):
        """
        [Functional Test] - TC05
        
        - Case: Check printed report when selecting multiple repair orders and click print Repair Report (PDF)
        - Expected Result: Report is printed, which contains data of selected repair orders
        """
        selected_repair_orders = self.env['repair.order']
        selected_repair_orders |= self.repair1
        selected_repair_orders |= self.repair2
        selected_repair_orders |= self.repair3
        selected_repair_orders |= self.repair4
        selected_repair_orders |= self.repair5
        
        pdf = self.env.ref('to_repair_extend.to_report_repair').render_qweb_pdf(selected_repair_orders.ids)
        tree = html.fromstring(pdf[0])
        # Compare row 1
        repair1_date_value = tree.xpath("//table/tbody/tr[1]/td[2]/span")[0].text
        repair1_service_name = tree.xpath("//table/tbody/tr[1]/td[3]/span")[0].text
        repair1_part_name1 = tree.xpath("//table/tbody/tr[1]/td[4]/span[1]")[0].text
        repair1_part_name2 = tree.xpath("//table/tbody/tr[1]/td[4]/span[2]")[0].text
        repair1_part_code1 = tree.xpath("//table/tbody/tr[1]/td[5]/span[1]")[0].text
        repair1_part_code2 = tree.xpath("//table/tbody/tr[1]/td[5]/span[2]")[0].text
        self.assertEqual(self.repair1.repair_date, fields.Date.from_string(repair1_date_value))
        self.assertEqual(self.repair1.fees_lines[0].product_id.name, repair1_service_name)
        self.assertTrue(set([repair1_part_name1, repair1_part_name2]) == set(self.repair1.operations.product_id.mapped('name')))
        self.assertTrue(set([repair1_part_code1, repair1_part_code2]) == set(self.repair1.operations.product_id.mapped('default_code')))
        
        # Compare row 2
        repair2_date_value = tree.xpath("//table/tbody/tr[2]/td[2]/span")[0].text
        repair2_service_name = tree.xpath("//table/tbody/tr[2]/td[3]/span")[0].text
        repair2_part_name1 = tree.xpath("//table/tbody/tr[2]/td[4]/span[1]")[0].text
        repair2_part_name2 = tree.xpath("//table/tbody/tr[2]/td[4]/span[2]")[0].text
        repair2_part_code1 = tree.xpath("//table/tbody/tr[2]/td[5]/span[1]")[0].text
        repair2_part_code2 = tree.xpath("//table/tbody/tr[2]/td[5]/span[2]")[0].text
        self.assertEqual(self.repair2.repair_date, fields.Date.from_string(repair2_date_value))
        self.assertEqual(self.repair2.fees_lines[0].product_id.name, repair2_service_name)
        self.assertTrue(set([repair2_part_name1, repair2_part_name2]) == set(self.repair2.operations.product_id.mapped('name')))
        self.assertTrue(set([repair2_part_code1, repair2_part_code2]) == set(self.repair2.operations.product_id.mapped('default_code')))
        
        # Compare row 3
        repair3_date_value = tree.xpath("//table/tbody/tr[3]/td[2]/span")[0].text
        repair3_service_name = tree.xpath("//table/tbody/tr[3]/td[3]/span")[0].text
        repair3_part_name1 = tree.xpath("//table/tbody/tr[3]/td[4]/span[1]")[0].text
        repair3_part_name2 = tree.xpath("//table/tbody/tr[3]/td[4]/span[2]")[0].text
        repair3_part_code1 = tree.xpath("//table/tbody/tr[3]/td[5]/span[1]")[0].text
        repair3_part_code2 = tree.xpath("//table/tbody/tr[3]/td[5]/span[2]")[0].text
        self.assertEqual(self.repair3.repair_date, fields.Date.from_string(repair3_date_value))
        self.assertEqual(self.repair3.fees_lines[0].product_id.name, repair3_service_name)
        self.assertTrue(set([repair3_part_name1, repair3_part_name2]) == set(self.repair3.operations.product_id.mapped('name')))
        self.assertTrue(set([repair3_part_code1, repair3_part_code2]) == set(self.repair3.operations.product_id.mapped('default_code')))
        
        # Compare row 4
        repair4_date_value = tree.xpath("//table/tbody/tr[4]/td[2]/span")[0].text
        repair4_service_name = tree.xpath("//table/tbody/tr[4]/td[3]/span")[0].text
        repair4_part_name1 = tree.xpath("//table/tbody/tr[4]/td[4]/span[1]")[0].text
        repair4_part_name2 = tree.xpath("//table/tbody/tr[4]/td[4]/span[2]")[0].text
        repair4_part_code1 = tree.xpath("//table/tbody/tr[4]/td[5]/span[1]")[0].text
        repair4_part_code2 = tree.xpath("//table/tbody/tr[4]/td[5]/span[2]")[0].text
        self.assertEqual(self.repair4.repair_date, fields.Date.from_string(repair4_date_value))
        self.assertEqual(self.repair4.fees_lines[0].product_id.name, repair4_service_name)
        self.assertTrue(set([repair4_part_name1, repair4_part_name2]) == set(self.repair4.operations.product_id.mapped('name')))
        self.assertTrue(set([repair4_part_code1, repair4_part_code2]) == set(self.repair4.operations.product_id.mapped('default_code')))
        
        # Compare row 5
        repair5_date_value = tree.xpath("//table/tbody/tr[5]/td[2]/span")[0].text
        repair5_service_name = tree.xpath("//table/tbody/tr[5]/td[3]/span")[0].text
        repair5_part_name1 = tree.xpath("//table/tbody/tr[5]/td[4]/span[1]")[0].text
        repair5_part_name2 = tree.xpath("//table/tbody/tr[5]/td[4]/span[2]")[0].text
        repair5_part_code1 = tree.xpath("//table/tbody/tr[5]/td[5]/span[1]")[0].text
        repair5_part_code2 = tree.xpath("//table/tbody/tr[5]/td[5]/span[2]")[0].text
        self.assertEqual(self.repair5.repair_date, fields.Date.from_string(repair5_date_value))
        self.assertEqual(self.repair5.fees_lines[0].product_id.name, repair5_service_name)
        self.assertTrue(set([repair5_part_name1, repair5_part_name2]) == set(self.repair5.operations.product_id.mapped('name')))
        self.assertTrue(set([repair5_part_code1, repair5_part_code2]) == set(self.repair5.operations.product_id.mapped('default_code')))
