from odoo.tests.common import SavepointCase


class Common(SavepointCase):

    @classmethod
    def setUpClass(cls):
        """
            Because all the demo project already has related demo tasks and timesheets
            We does not want to
                1) search / filtered for the WIP timesheet in every single test case
                2) unlink all the timesheets.
            Therefore:
                We just create 2 new task without any timesheet
        """
        super(Common, cls).setUpClass()
        cls.no_mailthread_features_ctx = {
            'no_reset_password': True,
            'tracking_disable': True,
        }
        cls.env = cls.env(context=dict(cls.no_mailthread_features_ctx, **cls.env.context))
        user_demo = cls.env.ref('base.user_demo')
        # Keep only Timesheet / Approver group for Demo user
        user_demo.write({'groups_id': [(6, 0, [cls.env.ref('hr_timesheet.group_hr_timesheet_approver').id])]})
        cls.user_demo = user_demo
        cls.user_admin = cls.env.ref('base.user_admin')

        # ----------> Project 1 <----------- #

        # Project Manager (user_id) = Marc Demo
        # allowed_timesheet = True
        # privacy_visibility = portal (invited portal users and all internal users)
        # Allowed_portal_user_ids consists of Joel Wills
        cls_project_office_design = cls.env.ref('project.project_project_1')

        # Marc Demo has 1 done timesheet
        cls.office_design_task1 = cls.env.ref('project.project_task_1')
        cls.office_design_task2 = cls.env.ref('project.project_task_6')

        # ----------> Project 2 <----------- #

        # Project Manager (user_id) = Marc Demo
        # allowed_timesheet = True
        # privacy_visibility = followers (invited internal users)
        # allowed_intenral_user_ids = False
        cls.project_r_d = cls.env.ref('project.project_project_2')

        # Mitchell Admin has 2 done timesheets
        # Marc Demo has 1 done timesheet
        # allowed_user_ids (Visbile To) = False
        cls.r_d_task1 = cls.env.ref('project.project_task_12')

        # Mitchell Admin has 0 done timesheets
        # Marc Demo has 1 done timesheet
        # allowed_user_ids (Visible To) = False
        cls.r_d_task2 = cls.env.ref('project.project_task_26')

        # Ensure there is no WIP timesheet to begin with
        domain = [
            ('employee_id', '!=', False),
            ('project_id', '!=', False),
            ('date_start', '!=', False),
            ('date_end', '=', False),
        ]
        cls.env['account.analytic.line'].sudo().search(domain).unlink()
