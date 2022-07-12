from odoo.tests import SavepointCase, Form


class TestRepairMaintenanceRequest(SavepointCase):
    
    @classmethod
    def setUpClass(cls):
        super(TestRepairMaintenanceRequest, cls).setUpClass()
        
        cls.product_to_repair = cls.env['product.product'].create({
            'name': 'Lenovo Thinkpad X1 carbon gen 4',
            'sale_ok': True,
            'purchase_ok': True,
            'can_be_equipment': True,
            'type': 'product',
            'categ_id': cls.env.ref('product.product_category_1').id,
            'tracking': 'serial',
        })
        cls.lot_serial = cls.env['stock.production.lot'].create({
            'name': 'LTPX1G4',
            'product_id': cls.product_to_repair.id,
            'company_id': cls.env.company.id
        })
        cls.milestone_1 = cls.env['product.milestone'].create({
            'name': 'Checking 3 weeks after bought',
            'amount': 3,
            'uom_id': cls.env.ref('to_uom_subscription.subscription_uom_week').id,
        })
        cls.maintenance_action = cls.env['maintenance.action'].create({
            'name': 'General health check',
            'service_id': cls.env.ref('repair.product_service_order_repair').id
        })
        cls.maintenance_schedule = cls.env['maintenance.schedule'].create({
            'part': 'First free official check and maintenance',
            'product_milestone_id': cls.milestone_1.id,
            'maintenance_action_id': cls.maintenance_action.id
        })
        
    def _create_equipment(self, schedule_ids=[]):
        """
            :param:    schedule_ids {list}: a list of record
        """
        updatable_schedule_ids = [(4, schedule.id) for schedule in schedule_ids] or False
        
        equipment = self.env['maintenance.equipment'].create({
            'name': 'Lenovo Thinkpad X1 carbon gen 4',
            'category_id': self.env.ref('maintenance.equipment_computer').id,
            'maintenance_team_id': self.env.ref('maintenance.equipment_team_maintenance').id,
            'technician_user_id': self.env.uid,
            'lot_id': self.lot_serial.id,
            'maintenance_schedule_ids': updatable_schedule_ids, 
        })
        
        return equipment
    
    def _create_and_save_repair_order(self, product_to_repair, maintenance_request, lot_serial):
        """
            Form is used here, because
            This module consists of method 'onchange_maintenance_request_id()'
        """
        form_repair_order = Form(self.env['repair.order'])
        form_repair_order.product_id = product_to_repair
        form_repair_order.maintenance_request_id = maintenance_request
        form_repair_order.lot_id = lot_serial
        form_repair_order.partner_id = self.env.ref('base.res_partner_address_13')
        repair_order = form_repair_order.save()
        
        return repair_order
    
    def _create_maintenance_request(self, equipment, milestone_id=False):
        val = {
            'name': 'Annual general checking',
            'employee_id': self.env.uid,
            'equipment_id': equipment.id,
            'request_date': '2021-10-05',
            'maintenance_type': 'preventive',
            'maintenance_team_id': self.env.ref('maintenance.equipment_team_maintenance').id,
            'user_id': self.env.uid,
            'schedule_date': '2021-10-06',
            'company_id': self.env.company.id,
        }
        if milestone_id:
            val['maintenance_milestone_id'] = milestone_id
            
        maintenance_request = self.env['maintenance.request'].create(val)
        return maintenance_request
    
    # ************************************************************* #
    # ************************ TEST CASES ************************* #
    # ************************************************************* #
    
    def test_00_no_milestone(self):
        """
            Input:
                Create equipment without milestone
                Create maintenance request without milestone
            Expect:
                Neither repair fee nor repair line is generated.
        """
        # Create equipment
        equipment = self._create_equipment()
        
        # Create maintenance request
        maintenance_request = self._create_maintenance_request(equipment)
    
        self.assertFalse(
            bool(maintenance_request.equipment_id.maintenance_schedule_ids),
            "There should be no milestone on this equipment."
        )
        self.assertFalse(
            bool(maintenance_request.maintenance_milestone_id),
            "There should be no milestone on this request."
        )
        
        # Rerturn a wizard
        repair_order_window_action = maintenance_request.repair_request_action()
        returned_request_id = repair_order_window_action['context']['default_maintenance_request_id']
         
        self.assertEqual(maintenance_request.id, returned_request_id)
    
        # Create repair order
        repair_order = self._create_and_save_repair_order(
            self.product_to_repair,
            maintenance_request,
            self.lot_serial
        )
    
        self.assertFalse(bool(repair_order.fees_lines))
        self.assertFalse(bool(repair_order.operations))
    
    def test_01_maintenance_request_different_milestones(self):
        """
            Input:
                Create equipment with milestone 1
                Create maintenance request with a milestone 2
            Expect:
                Neither repair fee nor repair line is generated.
        """
        # Create another milestone
        milestone_2 = self.env['product.milestone'].create({
            'name': 'PC Clean up',
            'amount': 3,
            'uom_id': self.env.ref('to_uom_subscription.uom_subscription_hour').id,
        })

        # Create equipment with milestone 1
        equipment = self._create_equipment([self.maintenance_schedule])
        
        # Create maintenance request with milestone 2
        maintenance_request = self._create_maintenance_request(
            equipment=equipment,
            milestone_id=milestone_2.id
        )
        maintenance_request.repair_request_action()
    
        # Create repair order
        repair_order = self._create_and_save_repair_order(
            self.product_to_repair,
            maintenance_request,
            self.lot_serial
        )
    
        self.assertFalse(bool(repair_order.fees_lines))
        self.assertFalse(bool(repair_order.operations))
    
    def test_02_maintenance_request_same_milestones(self):
        """
            Input:
                2 actions with Part_Replacement = True
                2 schedules with (Product) Part To Replace
                    the products are not type service
            Expect:
                Repair fees will be updated corresponding to product service 
                    of each maintenance schedule
                Repair lines will be updated corresponding to product replacement 
                    of each maintenance schedule.
        """
        # Replace Part products
        part_product_1 = self.env.ref('product.product_product_12')
        part_product_2 = self.env.ref('product.product_product_10')
    
        # This action does the Part Replacement
        self.maintenance_action.write({'part_replacement': True})
        # This schedule provides What the Replace Part for action 1 is
        self.maintenance_schedule.write({'product_id': part_product_1.id})
    
        # This action also does the Part Replacement
        maintenance_action_2 = self.env['maintenance.action'].create({
            'name': 'Replace part 2',
            'service_id': self.env.ref('repair.product_service_order_repair').id,
            'part_replacement': True,
        })
        # This schedule provides What the Replace Part for action 2 is
        maintenance_schedule_2 = self.env['maintenance.schedule'].create({
            'part': 'First free official check and extra service',
            'product_milestone_id': self.milestone_1.id,
            'maintenance_action_id': maintenance_action_2.id,
            'product_id': part_product_2.id,
        })
    
        # Create equipment
        equipment = self._create_equipment([self.maintenance_schedule, maintenance_schedule_2])
    
        # Create maintenance request
        maintenance_request = self._create_maintenance_request(
            equipment, 
            milestone_id=self.milestone_1.id
        )
        maintenance_request.repair_request_action()
    
        # Create repair order
        repair_order = self._create_and_save_repair_order(
            self.product_to_repair,
            maintenance_request,
            self.lot_serial
        )
    
        self.assertTrue(bool(repair_order.fees_lines))
        self.assertTrue(bool(repair_order.operations))
    
        self.assertEqual(len(repair_order.fees_lines), 2)
        self.assertEqual(len(repair_order.operations), 2)
    
        self.assertEqual(
            repair_order.fees_lines.product_id.id,
            maintenance_schedule_2.maintenance_action_id.service_id.id,
            "Product repair fee should be identical with the maintenance product service."
        )
    
        operations_product_ids = repair_order.operations.product_id.ids 
        self.assertTrue(
            maintenance_schedule_2.product_id.id in operations_product_ids,
            "Replace Part product should be presented as repair line in the repair order."
        )
        self.assertTrue(
            self.maintenance_schedule.product_id.id in operations_product_ids,
            "Replace Part product should be presented as repair line in the repair order."
        )
    
    def test_03_different_part_replace_condition(self):
        """
            Input:
                1 action with Part_Replacement = False
                1 action with Part_Replacement = True
    
                2 schedules with (Product) Part To Replace
            Expect:
                On the repair order:
                    Repair fees has 2 fee lines
                    Repair lines only has 1 line with the product part to replace that
                        has action with part_replacemnet = True
        """
        # Replace Part products
        part_product_1 = self.env.ref('product.product_product_12')
        part_product_2 = self.env.ref('product.product_product_10')
    
        # This action does NOT do the Part Replacement
        self.maintenance_action.write({'part_replacement': False})
        # But this schedule still provides What the Replace Part for action 1 is
        self.maintenance_schedule.write({'product_id': part_product_1.id})
        
        # This action does the Part Replacement
        maintenance_action_2 = self.env['maintenance.action'].create({
            'name': 'Replace part 2',
            'service_id': self.env.ref('repair.product_service_order_repair').id,
            'part_replacement': True,
        })
        # This schedule provides What the Replace Part for action 2 is
        maintenance_schedule_2 = self.env['maintenance.schedule'].create({
            'part': 'First free official check and extra service',
            'product_milestone_id': self.milestone_1.id,
            'maintenance_action_id': maintenance_action_2.id,
            'product_id': part_product_2.id,
        })
        
        # Create equipment
        equipment = self._create_equipment([self.maintenance_schedule, maintenance_schedule_2])
    
        # Create maintenance request
        maintenance_request = self._create_maintenance_request(
            equipment, 
            milestone_id=self.milestone_1.id
        )
        maintenance_request.repair_request_action()
    
        # Create repair order
        repair_order = self._create_and_save_repair_order(
            self.product_to_repair,
            maintenance_request,
            self.lot_serial
        )
    
        self.assertTrue(bool(repair_order.fees_lines))
        self.assertTrue(bool(repair_order.operations))
    
        self.assertEqual(len(repair_order.fees_lines), 2)
        self.assertEqual(len(repair_order.operations), 1)
    
        self.assertEqual(
            repair_order.fees_lines.product_id.id,
            maintenance_schedule_2.maintenance_action_id.service_id.id,
            "Product repair fee should be identical with the maintenance product service."
        )
        self.assertEqual(
            repair_order.operations.product_id.id,
            maintenance_schedule_2.product_id.id,
            "Product repair line should be identical with the Product part to replace."
        )
