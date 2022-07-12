from odoo import _
from odoo.tests import tagged
from odoo.exceptions import UserError

from .test_to_mrp_plm_common import TestPLMCommon

@tagged('post_install','-at_install')
class TestPLMFunction(TestPLMCommon):
# Test functional
#     =============================Apply on: BoM=================================
    """
        Case 1: Check number of aprovals after changing stages
    """
    def test_01_check_number_of_approvals(self):
        self.eco1.write({'stage_id': self.progress_stage.id})
        self.assertEqual(
            len(self.eco1.approval_ids),
            2,
            'Test error: number of approval is not true'
            )

    """
        Case 2: Check messages are commented
    """
    def test_02_check_message_commented(self):
        self.eco1.with_user(self.user_admin.id).message_post(
            body=_("We need some changes in this BoM."),
            message_type='comment'
            )
        approvals = self.eco1.approval_ids.filtered(lambda l: l.status == 'comment')
        self.assertTrue(
            approvals,
            'Test error: number of comment is not bigger than 1'
            )

    """
        Case 3: Check Approvals are approved
    """
    def test_03_check_approval_approved(self):
        self.eco1.write({'stage_id': self.progress_stage.id})
        self.eco1.with_user(self.user_demo.id).action_approve()
        approvals_approved = self.eco1.approval_ids.filtered(lambda l: l.status == 'approved')

        self.assertTrue(
            approvals_approved,
            'Test error: number of approve is not bigger than 0'
            )

        self.eco1.with_user(self.user_demo.id).action_reject()
        approvals_rejected = self.eco1.approval_ids.filtered(lambda l: l.status == 'rejected')

        self.assertTrue(
            approvals_rejected,
            'Test error: number of reject is not bigger than 0'
            )

    """
        Case 4: Check error message
    """
    def test_04_check_error_message(self):
        with self.assertRaises(UserError):
            self.eco1.write({'stage_id': self.validated_stage.id})

        self.eco1.write({'stage_id': self.progress_stage.id})
        with self.assertRaises(UserError):
            self.eco1.write({'stage_id': self.new_stage.id})

    """
        Case 5: Check BoM changed when press 'Start New Revision' button
    """
    def test_05_check_bom_changes_revision(self):
        self.eco1.action_new_revision()
        self.eco1.new_bom_id.bom_line_ids[2].update({'product_qty': 10})
        self.eco1.new_bom_id.bom_line_ids[3].update({'product_qty': 8})
        self.eco1.new_bom_id.operation_ids[0].update({'time_cycle_manual': 45})

        # At tab BoM changes, views the quantity of Bolt and Screw changed
        self.assertEqual(
            self.eco1.bom_change_ids[0].upd_product_qty,
            6,
            'Test error: number of bom changing is not true'
            )

        self.assertEqual(
            self.eco1.bom_change_ids[1].upd_product_qty,
            -2,
            'Test error: number of bom changing is not true'
            )
        # At tab Operations changes, field Manual Duration Change changed
        self.assertEqual(
            self.eco1.routing_change_ids[0].upd_time_cycle_manual,
            -15,
            'Test error: Operations changing is not true'
            )
        # Current BoM, quantity of Bolt and Screw do not change
        self.assertEqual(
            self.eco1.bom_id.bom_line_ids[2].product_qty,
            4,
            'Test error: number of bom changing is not true'
            )
        self.assertEqual(
            self.eco1.bom_id.bom_line_ids[3].product_qty,
            10,
            'Test error: number of bom changing is not true'
            )
        # The first operation of current BoM, field 'Time Cycle Manual' does not change
        self.assertEqual(
            self.eco1.bom_id.operation_ids[0].time_cycle_manual,
            60,
            'Test error: Operations changing is not true'
            )
        # New BoM changed
        self.assertEqual(
            self.eco1.new_bom_id.bom_line_ids[2].product_qty,
            10,
            'Test error: number of BoM changing is not true'
            )
        self.assertEqual(
            self.eco1.new_bom_id.bom_line_ids[3].product_qty,
            8,
            'Test error: number of BoM changing is not true'
            )
        # Current BoM is active
        self.assertTrue(
            self.eco1.bom_id.active,
            'Test error: Current BoM is archived')
        # New BoM is archived
        self.assertFalse(
            self.eco1.new_bom_id.active,
            'Test error: New BoM is active')

    """
        Case 6: Check new BoM version when press 'Apply Changes' button
    """

    def test_06_check_bom_changes_validate(self):
        self.eco1.action_new_revision()
        self.eco1.new_bom_id.bom_line_ids[2].update({'product_qty': 10})
        self.eco1.new_bom_id.bom_line_ids[3].update({'product_qty': 8})
        self.eco1.new_bom_id.operation_ids[0].update({'time_cycle_manual': 45})
        self.eco1.write({'stage_id': self.progress_stage.id})
        self.eco1.with_user(self.user_demo.id).action_approve()
        self.eco1.action_apply()

        # New BoM change
        self.assertEqual(
            self.eco1.new_bom_id.bom_line_ids[2].product_qty,
            10,
            'Test error: number of BoM changing is not true'
            )
        self.assertEqual(
            self.eco1.new_bom_id.bom_line_ids[3].product_qty,
            8,
            'Test error: number of BoM changing is not true'
            )
        # The first operation of new BoM, field 'Time Cycle Manual' changed
        self.assertEqual(
            self.eco1.new_bom_id.operation_ids[0].time_cycle_manual,
            45,
            'Test error: Operations changing is not true'
            )
        # Current BoM, quantity of Bolt and Screw do not change
        self.assertEqual(
            self.eco1.bom_id.bom_line_ids[2].product_qty,
            4,
            'Test error: number of bom changing is not true'
            )
        self.assertEqual(
            self.eco1.bom_id.bom_line_ids[3].product_qty,
            10,
            'Test error: number of bom changing is not true'
            )
        # The first operation of current BoM, field 'Time Cycle Manual' does not change
        self.assertEqual(
            self.eco1.bom_id.operation_ids[0].time_cycle_manual,
            60,
            'Test error: Operations changing is not true'
            )
        # Current BoM is archived
        self.assertFalse(
            self.eco1.bom_id.active,
            'Test error: Current BoM is active'
            )
        # New BoM is active
        self.assertTrue(
            self.eco1.new_bom_id.active,
            'Test error: New BoM is archived')
        # Check version of new BoM
        self.assertEqual(
            self.eco1.new_bom_id.version,
            1,
            'Test error: Version is not true'
            )

    """
        Case 7: Check new BoM version when create second ECO and press 'Apply Changes' button
    """

    def test_07_check_bom_changes_of_second_eco_apply_change(self):
        self.eco1.action_new_revision()
        self.eco1.new_bom_id.bom_line_ids[2].update({'product_qty': 10})
        self.eco1.new_bom_id.bom_line_ids[3].update({'product_qty': 8})
        self.eco1.new_bom_id.operation_ids[0].update({'time_cycle_manual': 45})
        self.eco1.write({'stage_id': self.progress_stage.id})
        self.eco1.with_user(self.user_demo.id).action_approve()
        self.eco1.write({'stage_id': self.validated_stage.id})
        self.eco1.action_apply()

        # Create eco2  apply on the same BoM of eco1
        eco2 = self.eco.create({
            'name': 'Change Funiture BoM 2',
            'stage_id': self.new_stage.id,
            'type_id': self.eco_type.id,
            'type': 'bom',
            'product_tmpl_id': self.bom_desk.product_tmpl_id.id,
            'bom_id':self.eco1.new_bom_id.id
            })
        eco2.action_new_revision()
        eco2.new_bom_id.bom_line_ids[1].update({'product_qty': 3})
        eco2.new_bom_id.operation_ids[0].update({'time_cycle_manual': 55})
        eco2.write({'stage_id': self.progress_stage.id})
        eco2.with_user(self.user_demo.id).action_approve()
        eco2.write({'stage_id': self.validated_stage.id})
        eco2.action_apply()

        # At tab BoM changes, views the quantity of Table leg changed
        self.assertEqual(
            eco2.bom_change_ids[0].upd_product_qty,
            -1,
            'Test error: BoM changing is not true'
            )
        # Current BoM does not change
        self.assertEqual(
            eco2.bom_id.bom_line_ids[1].product_qty,
            4,
            'Test error: BoM changing is not true'
            )
        # At tab Operations Changes, field 'Manual Duration Change' = 10
        self.assertEqual(
            eco2.routing_change_ids[0].upd_time_cycle_manual,
            10,
            'Test error: Routing changing is not true'
            )
        # The first operation of current BoM, field 'Time Cycle Manual' does not change
        self.assertEqual(
            eco2.bom_id.operation_ids[0].time_cycle_manual,
            45,
            'Test error: Operation changing is not true'
            )
        # Current BoM is archived
        self.assertFalse(
            eco2.bom_id.active,
            'Test error: Current BoM is active'
            )
        # New BoM is active
        self.assertTrue(
            eco2.new_bom_id.active,
            'Test error: New BoM is archived'
            )
        # Check new version
        self.assertEqual(
            eco2.new_bom_id.version,
            2,
            'Test error: Version is not True'
            )
        # Check version of new BoM
        self.assertEqual(
            eco2.new_bom_id.version,
            2,
            'Test error: Version is not true'
            )

    """
        Case 13: Configure ECO with BoM,
                 check ECO type
    """

    def test_08_check_approval_type(self):

        eco2 = self.eco.create({
            'name': 'Change Funiture Routing 2',
            'stage_id': self.new_stage.id,
            'type_id': self.eco_type.id,
            'type': 'bom',
            'product_tmpl_id': self.bom_desk.product_tmpl_id.id,
            'bom_id':self.bom_desk.id
            })
        eco2.write({'stage_id': self.progress_stage.id})
        eco2.with_user(self.user_demo.id).action_approve()
        eco2.write({'stage_id': self.validated_stage.id})

        self.eco1.write({'stage_id': self.progress_stage.id})

        self.eco1.action_new_revision()
        self.eco_type = self.eco_type.with_user(self.user_demo.id)
        # Total of ECOs group by type
        self.assertEqual(
            self.eco_type.nb_ecos,
            2,
            'Test error: count of ECOS is not true'
            )
        # My waiting Aprovals
        self.assertEqual(
            self.eco_type.nb_approvals_my,
            1,
            'Test error: count of ECOS is not true'
            )
        # Waiting Aprovals
        self.assertEqual(
            self.eco_type.nb_approvals,
            1,
            'Test error: count of ECOS is not true'
            )
        # To Apply: count when click New Revision and change stage to Validated
        self.assertEqual(
            self.eco_type.nb_validation,
            1,
            'Test error: count of ECOS is not true'
            )
