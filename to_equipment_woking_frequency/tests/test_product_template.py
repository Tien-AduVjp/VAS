from odoo.tests import TransactionCase, tagged
from odoo.exceptions import ValidationError

from . import ultils


@tagged('post_install', '-at_install')
class TestProductTemplate(TransactionCase):

    def setUp(self):
        super(TestProductTemplate, self).setUp()      
        self.WorkingFrequencyTemplateObj = self.env['working.frequency.template']
        self.product_uom_kgm_id = self.ref('uom.product_uom_kgm')      
        self.product_uom_gram_id = self.ref('uom.product_uom_gram')  
        self.product_uom_meter_id = self.ref('uom.product_uom_meter')      
        self.product_uom_day_id = self.ref('uom.product_uom_day')   
        self.product_working_frequency_kgm = self.WorkingFrequencyTemplateObj.create({       
            'working_amount':ultils.WORKING_AMOUNT,
            'working_uom_id': self.product_uom_kgm_id,
            'period_time':ultils.PERIOD_TIME,
            'period_time_uom_id':self.product_uom_day_id
        })
        self.product_working_frequency_gram_data = {            
            'working_amount':ultils.WORKING_AMOUNT,
            'working_uom_id': self.product_uom_gram_id,
            'period_time':ultils.PERIOD_TIME,
            'period_time_uom_id':self.product_uom_day_id
        }
        self.product_working_frequency_meter_data = {       
            'working_amount':ultils.WORKING_AMOUNT,
            'working_uom_id': self.product_uom_meter_id,
            'period_time':ultils.PERIOD_TIME,
            'period_time_uom_id':self.product_uom_day_id
        }   
        self.product = self.env['product.product'].create({
            'name':'Product Test',
            'working_frequency_template_ids':[(6, 0, [self.product_working_frequency_kgm.id])]
        })
        
    def test_check_working_frequency_template_ids(self):
        """
            Check unique Unit of Measure category working frequency category in one product.
        """
        # Test case1:Add difference Unit of Measure category working frequency for product
        add_working_frequency_meter = self.product.write({
                'working_frequency_template_ids':[(0, 0, self.product_working_frequency_meter_data
                )]
            })
        self.assertTrue(add_working_frequency_meter, "Can add difference Unit of measure category")
        # Test case2:Add same Unit of Measure category working frequency in one product.
        with self.assertRaises(ValidationError): 
            self.product.update({
                'working_frequency_template_ids':[(0, 0, self.product_working_frequency_gram_data
                )]
            })
