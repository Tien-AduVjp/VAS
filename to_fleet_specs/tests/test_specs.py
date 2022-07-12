from datetime import datetime, timedelta

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestSpecs(TransactionCase):
    
    def setUp(self):
        super(TestSpecs, self).setUp()
                
        model_vehicle = self.env.ref('fleet.brand_audi')
        
        self.bus_13_29_vehicle = self.env['fleet.vehicle'].create({
                'model_id': model_vehicle.id,
                'class_id': self.ref('to_fleet_specs.bus_13_29_seats')
            })
        
        self.truck_2_4_tons_vehicle = self.env['fleet.vehicle'].create({
                'model_id': model_vehicle.id,
                'class_id': self.ref('to_fleet_specs.truck_2_4_tons')
            })

    def test_check_seats_class_id(self):
        """
        This test ensures the given seats of vehicle satisfying its constraint: value in class.min_seats ~ class.max_seats
        """
        self.truck_2_4_tons_vehicle.seats = 13
        self.truck_2_4_tons_vehicle.seats = 29
        
        with self.assertRaises(ValidationError):
            self.bus_13_29_vehicle.write({'seats': 12})
            
        with self.assertRaises(ValidationError):
            self.bus_13_29_vehicle.write({'seats': 30})
               
    def test_check_self_weight_class_id(self):
        """
        This test ensures the given self_weight of vehicle satisfying its constraint: value in class.min_weight ~ class.max_weight
        """
        self.truck_2_4_tons_vehicle.self_weight = 2000
        self.truck_2_4_tons_vehicle.self_weight = 4000
        
        with self.assertRaises(ValidationError):
            self.truck_2_4_tons_vehicle.write({'self_weight': 1999})
            
        with self.assertRaises(ValidationError):
            self.truck_2_4_tons_vehicle.write({'self_weight': 4001})

    def test_check_year_made(self):
        """
        This test ensures the given year_made of vehicle satisfying its constraint: value in 1900 ~ today
        """
        self.truck_2_4_tons_vehicle.year_made = 1900
        self.truck_2_4_tons_vehicle.year_made = datetime.today().year
        next_year = (datetime.today() + timedelta(days=365)).year

        with self.assertRaises(ValidationError):
            self.truck_2_4_tons_vehicle.write({'year_made': 1899})
            
        with self.assertRaises(ValidationError):
            self.truck_2_4_tons_vehicle.write({'year_made': next_year})
        
    def test_check_negative_trailer_inner(self):
        """
        This test ensures the given trailer_inner of vehicle satisfying its constraint: not negative
        """
        self.truck_2_4_tons_vehicle.trailer_inner_height = 0
        self.truck_2_4_tons_vehicle.trailer_inner_height = 0
        self.truck_2_4_tons_vehicle.trailer_inner_height = 0

        with self.assertRaises(ValidationError):
            self.truck_2_4_tons_vehicle.write({'trailer_inner_height': -1})
            
        with self.assertRaises(ValidationError):
            self.truck_2_4_tons_vehicle.write({'trailer_inner_width': -1})

        with self.assertRaises(ValidationError):
            self.truck_2_4_tons_vehicle.write({'trailer_inner_length': -1})
