from odoo.tests import tagged

from odoo.addons.viin_user_assignment_log.tests.common import TestUserAssignmentLogCommon


@tagged('post_install', '-at_install')
class TestEmployeeAssignmentLogIrcron(TestUserAssignmentLogCommon):

    def setUp(self):
        super(TestEmployeeAssignmentLogIrcron, self).setUp()
        self.employee_user_main_comp.with_company(self.employee_user_main_comp.company_id).with_context(
            tracking_disable=True
            ).action_create_employee()
        self.employee_user_comp_B.with_company(self.employee_user_comp_B.company_id).with_context(
            tracking_disable=True
            ).action_create_employee()
        self.employee_main_comp = self.employee_user_main_comp.employee_id
        self.employee_comp_B = self.employee_user_comp_B.employee_id

    def test_model_01_log_ir_cron(self):
        """
            On a record "autovacuum_job":
            1) Assign 'user_id' field to user Main
                => A new record 'UA1' is generated on User Assignment model with:
                    'user_id'                 =     id of user Main
                    'assigned_by_user_id'     =     id of user admin
                    'employee_id'             =     id of user Main's employee

            2) Re-assign 'user_id' to user B
                => Update 'UA1':
                    'unassigned_by_user_id'   =     id of user B
                => A new record is generated on User Assignment with:
                    'user_id'                 =     id of user Main
                    'assigned_by_user_id'     =     id of user admin
                    'employee_id'             =     id of user Main's employee
        """

        self.autovacuum_job.with_user(self.user_admin).write({'user_id': self.employee_user_main_comp.id})

        log_assign_user = self.env['user.assignment'].search([
            ('user_id', '=', self.employee_user_main_comp.id),
            ('assigned_by_user_id', '=', self.user_admin.id),
            ('employee_id', '=', self.employee_main_comp.id)
        ])

        self.assertTrue(
            bool(log_assign_user),
            "Error testing: update user_id field on a record of model ir.cron should generate a User Assignment log."
        )

        self.autovacuum_job.with_user(self.user_admin).write({'user_id': self.employee_user_comp_B.id})
        log_assign_user_after_reassign = self.env['user.assignment'].search([
            ('user_id', '=', self.employee_user_main_comp.id),
            ('assigned_by_user_id', '=', self.user_admin.id),
            ('unassigned_by_user_id', '=', self.user_admin.id),
            ('employee_id', '=', self.employee_main_comp.id)
        ])

        self.assertTrue(
            bool(log_assign_user_after_reassign),
            "Error testing: re-update user_id should assign value on 'unassigned_by_user_id' field."
        )

        log_reassign_user_1 = self.env['user.assignment'].search([
            ('user_id', '=', self.employee_user_comp_B.id),
            ('assigned_by_user_id', '=', self.user_admin.id),
            ('employee_id', '=', self.employee_comp_B.id)
        ])

        self.assertTrue(
            bool(log_reassign_user_1),
            "Error testing: re-update user_id field on a record of model ir.cron should generate a new User Assignment log."
        )

    def test_model_02_model_log_ir_cron_employee_multi_company(self):
        """
            Create a user that belongs to 2 companies
            On record 'autovacuum_job', assign this user to user_id. This will generate a new record (UA_1) of model User Assignment.

                Before, the autovacuum_job has company_id = id of company Main
                => UA_1 should be generated with the same company_id
                => UA_1 should not be generated with company_id = id of company B
        """

        self.employee_user_comp_B.write({'company_ids': [(4, self.main_company.id)]})
        self.autovacuum_job.with_user(self.user_admin).write({'user_id': self.employee_user_comp_B.id})

        log_assign_user_main_comp = self.env['user.assignment'].search([
            ('user_id', '=', self.employee_user_comp_B.id),
            ('assigned_by_user_id', '=', self.user_admin.id),
            ('company_id', '=', self.main_company.id),
            ('employee_id', '=', self.employee_comp_B.id)
        ])
        log_assign_user_B_comp = self.env['user.assignment'].search([
            ('user_id', '=', self.employee_user_comp_B.id),
            ('assigned_by_user_id', '=', self.user_admin.id),
            ('company_id', '=', self.company_B.id),
            ('employee_id', '=', self.employee_comp_B.id)
        ])

        self.assertTrue(
            bool(log_assign_user_main_comp),
            ("Error testing: this record of User Assignment should STILL be generated for company Main, "
             "since the record of ir.cron still belongs to company Main."))
        self.assertFalse(
            bool(log_assign_user_B_comp),
            ("Error testing: this record of User Assignment should NOT be generated for company Main, "
             "since the record of ir.cron still belongs to company Main."))

    def test_model_03_employee_assignment_blacklisted_models(self):
        """
            No record of User Assignment will be generated if the being-processed model is on the blacklist
        """

        # Replace the content of this function in base for testing purpose
        blacklist = self.env['base']._get_user_assignment_backlisted_models()
        blacklist.append('ir.cron')
        self.patch(type(self.env['base']), '_get_user_assignment_backlisted_models', lambda self: blacklist)

        # Begin testing
        self.autovacuum_job.with_user(self.user_admin).write({'user_id': self.employee_user_main_comp.id})

        log_assign_user = self.env['user.assignment'].search([
            ('user_id', '=', self.employee_user_main_comp.id),
            ('assigned_by_user_id', '=', self.user_admin.id),
            ('employee_id', '=', self.employee_main_comp.id)
        ])
        self.assertFalse(
            bool(log_assign_user),
            ("Error testing: This model ir.cron is blacklisted. "
            "Hence, updating user_id field on a record of this model should NOT generate a User Assignment log.")
        )
