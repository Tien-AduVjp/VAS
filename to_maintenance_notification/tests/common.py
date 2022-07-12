from datetime import timedelta

from odoo import fields
from odoo.tests import TransactionCase


class Common(TransactionCase):
    def setUp(self):
        super(Common,self).setUp()

        self.milestone_100,self.milestone_800,self.milestone_1000,self.milestone_by_hours_100 = self.env['product.milestone'].create([
             # UoM milestone_100, milestone_800, milestone_1000 DOES NOT BELONG to category of WORKING TIME.
            {
                'name':'MileStone 100 Units',
                'amount':100.0,
                'uom_id':self.ref('uom.product_uom_unit')
            },
            {
                'name':'MileStone 800 Units',
                'amount':800.0,
                'uom_id':self.ref('uom.product_uom_unit')
            },
            {
                'name':'MileStone 1000 Units',
                'amount':1000.0,
                'uom_id':self.ref('uom.product_uom_unit')
            },
            # UoM milestone_by_hours IS BELONG to category of WORKING TIME.
            {
                'name':'MileStone 100 Hours',
                'amount':100.0,
                'uom_id':self.ref('uom.product_uom_hour'),
            }
        ])
        self.product_service = self.env['product.product'].create({
            'name':'Maintenance Product Service',
            'type':'service'
        })
        self.maintenance_action = self.env['maintenance.action'].create({
            'name':'Maintenance Action',
            'service_id':self.product_service.id
        })
        self.maintenance_schedule_part_01,self.maintenance_schedule_part_02,self.maintenance_schedule_part_03,self.maintenance_schedule_part_04\
        = self.env['maintenance.schedule'].create([
            {
                'part':'Part maintenance after 100 unit working',
                'product_milestone_id':self.milestone_100.id,
                'maintenance_action_id':self.maintenance_action.id
            },
            {
                'part':'Part maintenance after 800 unit working',
                'product_milestone_id':self.milestone_800.id,
                'maintenance_action_id':self.maintenance_action.id
            },
            {
                'part':'Part maintenance after 1000 unit working',
                'product_milestone_id':self.milestone_1000.id,
                'maintenance_action_id':self.maintenance_action.id
            },
            {
                'part':'Part maintenance after 100 hours working',
                'product_milestone_id':self.milestone_by_hours_100.id,
                'maintenance_action_id':self.maintenance_action.id
            }
        ])
        self.equipment_working_frequency = self.env['equipment.working.frequency'].create({
            'start_amount':20,
            'working_amount':420,
            'working_uom_id':self.ref('uom.product_uom_unit'),
            'period_time':7.0,
        })

        self.equipment_category_test_01 = self.env['maintenance.equipment.category'].create({
            'name':'Equipment Category Test 01',
            'days_to_notify':7
        })
        self.equipment_test_01 = self.env['maintenance.equipment'].create({
            'name':'Equipment Test 01',
            'effective_date':fields.date.today() - timedelta(days = 1),
            'category_id':self.equipment_category_test_01.id,
            'preventive_maintenance_mode': 'schedule'
        })
