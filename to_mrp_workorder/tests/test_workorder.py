from odoo.tests.common import TransactionCase, tagged, Form

from odoo.addons.mrp.tests.common import TestMrpCommon


@tagged('post_install', '-at_install')
class TestMrpWorkorder(TestMrpCommon):

    def setUp(self):
        super(TestMrpWorkorder, self).setUp()
        self.product_6_bom = self.env['mrp.bom'].create({
            'product_id': self.product_6.id,
            'product_tmpl_id': self.product_6.product_tmpl_id.id,
            'product_qty': 1,
            'product_uom_id': self.product_6.uom_id.id,
            'consumption': 'flexible',
            'type': 'normal',
            'bom_line_ids': [
                (0, 0, {'product_id': self.product_2.id, 'product_qty': 2.00}),
            ],
            'operation_ids': [
                (0, 0, {
                    'name': 'Do it',
                    'workcenter_id': self.workcenter_2.id,
                    'time_mode_batch': 1,
                    'time_mode': 'auto',
                    'sequence': 1
                }),
            ]
        })

    def test_tablet_validate_mo_without_backorder(self):
        """
            Test validate MO with only 1 final product, no backorder
        """
        # Create MO for product_6
        mo_form = Form(self.env['mrp.production'])
        mo_form.product_id = self.product_6
        mo_form.bom_id = self.product_6_bom
        mo_form.product_qty = 1
        mo_form.product_uom_id = self.product_6.uom_id
        mo = mo_form.save()
        mo.action_confirm()

        # Validate MO with tablet validate action on work order
        self.assertEqual(len(mo.workorder_ids), 1)
        mo.workorder_ids.button_start()
        mo.workorder_ids.action_tablet_validate()

        # Check MO
        self.assertEqual(mo.state, 'done')
        self.assertEqual(mo.qty_produced, 1)

    def test_tablet_validate_mo_with_backorder(self):
        """
            Test validate MO with backorder
        """
        # Create MO for product_6
        mo_form = Form(self.env['mrp.production'])
        mo_form.product_id = self.product_6
        mo_form.bom_id = self.product_6_bom
        mo_form.product_qty = 3
        mo_form.product_uom_id = self.product_6.uom_id
        mo = mo_form.save()
        mo.action_confirm()

        # Validate MO with tablet validate action on work order
        self.assertEqual(len(mo.workorder_ids), 1)
        mo.workorder_ids.button_start()
        mo.workorder_ids.qty_producing = 1
        action = mo.workorder_ids.action_tablet_validate()
        self.assertEqual(action.get('res_model'), 'mrp.production.backorder')
        wizard = Form(self.env[action['res_model']].with_context(action['context'])).save()
        action = wizard.action_backorder()

        # Check if backorder is generated
        backorder_wo = self.env['mrp.workorder'].browse(action['res_id'])
        self.assertEqual(len(backorder_wo.production_id.procurement_group_id.mrp_production_ids), 2)

        # Check MO backorder
        mo_backorder = backorder_wo.production_id.procurement_group_id.mrp_production_ids[-1]
        self.assertEqual(mo_backorder.product_qty, 2)
        self.assertEqual(sum(mo_backorder.move_raw_ids.filtered(lambda m: m.product_id.id == self.product_2.id).mapped("product_uom_qty")), 4)

    def test_tablet_create_backorder(self):
        """
            Test create back order without validate MO
        """
        # Create MO for product_6
        mo_form = Form(self.env['mrp.production'])
        mo_form.product_id = self.product_6
        mo_form.bom_id = self.product_6_bom
        mo_form.product_qty = 3
        mo_form.product_uom_id = self.product_6.uom_id
        mo = mo_form.save()
        mo.action_confirm()

        # Validate MO with tablet validate action on work order
        mo_form = Form(self.env['mrp.production'])
        self.assertEqual(len(mo.workorder_ids), 1)
        mo.workorder_ids[0].button_start()
        mo.workorder_ids[0].qty_producing = 1
        mo.workorder_ids[0].action_tablet_record_production()

        # Check current MO
        self.assertEqual(mo.state, 'progress')
        self.assertEqual(mo.workorder_ids[0].state, 'progress')

        # Check backorder
        mo_backorder = mo.procurement_group_id.mrp_production_ids[-1]
        self.assertEqual(mo_backorder.product_qty, 2)
        self.assertEqual(sum(mo_backorder.move_raw_ids.filtered(lambda m: m.product_id.id == self.product_2.id).mapped("product_uom_qty")), 4)
