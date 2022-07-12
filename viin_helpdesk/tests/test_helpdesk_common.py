from odoo import fields
from dateutil.relativedelta import relativedelta
from odoo.tests.common import SavepointCase


class TestHelpdeskCommon(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestHelpdeskCommon, cls).setUpClass()

        cls.no_mailthread_features_ctx = {
            'no_reset_password': True,
            'tracking_disable': True,
        }
        cls.env = cls.env(context=dict(cls.no_mailthread_features_ctx, **cls.env.context))

        user_group_employee = cls.env.ref('base.group_user')
        user_group_helpdesk_user = cls.env.ref('viin_helpdesk.group_helpdesk_user')
        user_group_helpdesk_manager = cls.env.ref('viin_helpdesk.group_helpdesk_manager')

        cls.partner_1 = cls.env['res.partner'].create({
            'name': 'Valid Lelitre',
            'email': 'valid.lelitre@agrolait.com'})
        cls.partner_2 = cls.env['res.partner'].create({
            'name': 'Valid Poilvache',
            'email': 'valid.other@example.viindoo.com'})

        # Test users to use through the various tests
        Users = cls.env['res.users']
        cls.user_public = Users.create({
            'name': 'Bert Tartignole',
            'login': 'bert',
            'email': 'b.t@example.viindoo.com',
            'signature': 'SignBert',
            'notification_type': 'email',
            'groups_id': [(6, 0, [cls.env.ref('base.group_public').id])]})
        cls.user_portal = Users.create({
            'name': 'Chell Gladys',
            'login': 'chell',
            'email': 'chell@gladys.portal',
            'signature': 'SignChell',
            'notification_type': 'email',
            'groups_id': [(6, 0, [cls.env.ref('base.group_portal').id])]})

        cls.user_employee_user = Users.create({
            'name': 'Anton EmployeeUser',
            'login': 'AntonEmployee',
            'email': 'anton.employeeuser@example.viindoo.com',
            'groups_id': [(6, 0, [user_group_employee.id])]
        })

        cls.user_member_user = Users.create({
            'name': 'Anna MemberUser',
            'login': 'AnnaMember',
            'email': 'anna.memberuser@example.viindoo.com',
            'groups_id': [(6, 0, [user_group_employee.id, user_group_helpdesk_user.id])]
        })

        cls.user_leader_user = Users.create({
            'name': 'Anna LeaderUser',
            'login': 'AnnaLeader',
            'email': 'anna.leaderuser@example.viindoo.com',
            'groups_id': [(6, 0, [user_group_employee.id, user_group_helpdesk_user.id])]
        })

        cls.user_helpdesk_user = Users.create({
            'name': 'Armande HelpdeskUser',
            'login': 'Armande',
            'email': 'armande.helpdeskuser@example.viindoo.com',
            'groups_id': [(6, 0, [user_group_employee.id, user_group_helpdesk_user.id])]
        })
        cls.user_helpdesk_manager = Users.create({
            'name': 'Bastien HelpdeskManager',
            'login': 'bastien',
            'email': 'bastien.helpdeskmanager@example.viindoo.com',
            'groups_id': [(6, 0, [user_group_employee.id, user_group_helpdesk_manager.id])]})

        cls.new_stage = cls.env['helpdesk.stage'].create({'name': 'New_Stage', 'sequence': 10})
        cls.assigned_stage = cls.env['helpdesk.stage'].create({'name': 'New_Stage', 'sequence': 20})
        cls.empty_stage = cls.env['helpdesk.stage'].create({'name': 'Empty Stage'})

        cls.tag = cls.env['helpdesk.tag'].create({'name': 'Tag Test'})
        # Test 'General' team
        cls.team_general = cls.env['helpdesk.team'].with_context({'mail_create_nolog': True}).create({
            'name': 'General Team',
            'privacy_visibility': 'employees',
            'team_leader_id': cls.user_leader_user.id,
            'company_id': cls.env.company.id,
            'team_member_ids': [(6, 0, [cls.user_member_user.id, cls.user_helpdesk_user.id, cls.user_leader_user.id])],
            'stage_ids': [(6, 0, [cls.new_stage.id, cls.assigned_stage.id])]
            })

        cls.env.company.default_helpdesk_team_id.stage_ids = [(4, cls.env.ref('viin_helpdesk.helpdesk_stage_resolved').id)]

        # Already-existing tasks in Pigs
        cls.ticket_public = cls.env['helpdesk.ticket'].with_user(cls.user_public).with_context({'mail_create_nolog': True}).sudo().create({
            'name': 'General TicketPublic',
            'user_id': cls.user_member_user.id,
            'team_id': cls.team_general.id})

        cls.ticket_portal = cls.env['helpdesk.ticket'].with_user(cls.user_portal).with_context({'mail_create_nolog': True}).sudo().create({
            'name': 'General TicketPortal',
            'user_id': cls.user_member_user.id,
            'team_id': cls.team_general.id})

        cls.ticket_employee = cls.env['helpdesk.ticket'].with_user(cls.user_employee_user).with_context({'mail_create_nolog': True}).create({
            'name': 'General TicketEmployee',
            'user_id': cls.user_member_user.id,
            'team_id': cls.team_general.id})

        cls.ticket_user = cls.env['helpdesk.ticket'].with_user(cls.user_member_user).with_context({'mail_create_nolog': True}).create({
            'name': 'General TicketUser',
            'user_id': cls.user_member_user.id,
            'team_id': cls.team_general.id})

        cls.ticket_leader = cls.env['helpdesk.ticket'].with_user(cls.user_leader_user).with_context({'mail_create_nolog': True}).create({
            'name': 'General TicketLeader',
            'user_id': cls.user_member_user.id,
            'team_id': cls.team_general.id})

    def _prepare_digest_ticket_data(self):
        company = self.env.company.id
        today = fields.date.today()
        yesterday = today - relativedelta(days=1)
        lastweek = today - relativedelta(days=7)
        lastmonth = today - relativedelta(months=1)

        # Create Stages for Tickets
        self.final_stage_false = self.env['helpdesk.stage'].create({
            'name': 'Done',
            'is_final_stage': False
            })

        self.stage_fold_false = self.env['helpdesk.stage'].create({
            'name': 'Done',
            'fold': False,
            })

        self.final_stage_true = self.env['helpdesk.stage'].create({
            'name': 'Done',
            'is_final_stage': True
            })

        self.stage_fold_true = self.env['helpdesk.stage'].create({
            'name': 'Done',
            'fold': True
            })

        # Create Tickets OPENED
        self.ticket_opened_1 = self.env['helpdesk.ticket'].create({
            'name': 'Ticket 1',
            'user_id': self.user_member_user.id,
            'team_id': self.team_general.id,
            'company_id': company,
            'stage_id': self.final_stage_false.id,
            })
        self.env.cr.execute("""UPDATE helpdesk_ticket SET create_date = %s WHERE id = %s""", (yesterday, self.ticket_opened_1.id))
        self.ticket_opened_1.invalidate_cache()

        self.ticket_opened_2 = self.env['helpdesk.ticket'].create({
            'name': 'Ticket 2',
            'user_id': self.user_member_user.id,
            'team_id': self.team_general.id,
            'company_id': company,
            'stage_id': self.stage_fold_false.id,
            })
        self.env.cr.execute("""UPDATE helpdesk_ticket SET create_date = %s WHERE id = %s""", (yesterday, self.ticket_opened_2.id))
        self.ticket_opened_2.invalidate_cache()

        self.ticket_opened_3 = self.env['helpdesk.ticket'].create({
            'name': 'Ticket 3',
            'user_id': self.user_member_user.id,
            'team_id': self.team_general.id,
            'company_id': company,
            'stage_id': self.final_stage_false.id,
            })
        self.env.cr.execute("""UPDATE helpdesk_ticket SET create_date = %s WHERE id = %s""", (lastweek, self.ticket_opened_3.id))
        self.ticket_opened_3.invalidate_cache()

        self.ticket_opened_4 = self.env['helpdesk.ticket'].create({
            'name': 'Ticket 4',
            'user_id': self.user_member_user.id,
            'team_id': self.team_general.id,
            'company_id': company,
            'stage_id': self.stage_fold_false.id,
            })
        self.env.cr.execute("""UPDATE helpdesk_ticket SET create_date = %s WHERE id = %s""", (lastweek, self.ticket_opened_4.id))
        self.ticket_opened_4.invalidate_cache()

        self.ticket_opened_5 = self.env['helpdesk.ticket'].create({
            'name': 'Ticket 5',
            'user_id': self.user_member_user.id,
            'team_id': self.team_general.id,
            'company_id': company,
            'stage_id': self.final_stage_false.id,
            })
        self.env.cr.execute("""UPDATE helpdesk_ticket SET create_date = %s WHERE id = %s""", (lastmonth, self.ticket_opened_5.id))
        self.ticket_opened_5.invalidate_cache()

        self.ticket_opened_6 = self.env['helpdesk.ticket'].create({
            'name': 'Ticket 6',
            'user_id': self.user_member_user.id,
            'team_id': self.team_general.id,
            'company_id': company,
            'stage_id': self.stage_fold_false.id,
            })
        self.env.cr.execute("""UPDATE helpdesk_ticket SET create_date = %s WHERE id = %s""", (lastmonth, self.ticket_opened_6.id))
        self.ticket_opened_6.invalidate_cache()

        # Create Tickets CLOSED
        self.ticket_closed_1 = self.env['helpdesk.ticket'].create({
            'name': 'Ticket 7',
            'user_id': self.user_member_user.id,
            'team_id': self.team_general.id,
            'company_id': company,
            'stage_id': self.final_stage_true.id,
            })
        self.env.cr.execute("""UPDATE helpdesk_ticket SET create_date = %s WHERE id = %s""", (yesterday, self.ticket_closed_1.id))
        self.ticket_closed_1.invalidate_cache()

        self.ticket_closed_2 = self.env['helpdesk.ticket'].create({
            'name': 'Ticket 8',
            'user_id': self.user_member_user.id,
            'team_id': self.team_general.id,
            'company_id': company,
            'stage_id': self.stage_fold_true.id,
            })
        self.env.cr.execute("""UPDATE helpdesk_ticket SET create_date = %s WHERE id = %s""", (yesterday, self.ticket_closed_2.id))
        self.ticket_closed_2.invalidate_cache()

        self.ticket_closed_3 = self.env['helpdesk.ticket'].create({
            'name': 'Ticket 9',
            'user_id': self.user_member_user.id,
            'team_id': self.team_general.id,
            'company_id': company,
            'stage_id': self.final_stage_true.id,
            })
        self.env.cr.execute("""UPDATE helpdesk_ticket SET create_date = %s WHERE id = %s""", (lastweek, self.ticket_closed_3.id))
        self.ticket_closed_3.invalidate_cache()

        self.ticket_closed_4 = self.env['helpdesk.ticket'].create({
            'name': 'Ticket 10',
            'user_id': self.user_member_user.id,
            'team_id': self.team_general.id,
            'company_id': company,
            'stage_id': self.stage_fold_true.id,
            })
        self.env.cr.execute("""UPDATE helpdesk_ticket SET create_date = %s WHERE id = %s""", (lastweek, self.ticket_closed_4.id))
        self.ticket_closed_4.invalidate_cache()

        self.ticket_closed_5 = self.env['helpdesk.ticket'].create({
            'name': 'Ticket 11',
            'user_id': self.user_member_user.id,
            'team_id': self.team_general.id,
            'company_id': company,
            'stage_id': self.final_stage_true.id,
            })
        self.env.cr.execute("""UPDATE helpdesk_ticket SET create_date = %s WHERE id = %s""", (lastmonth, self.ticket_closed_5.id))
        self.ticket_closed_5.invalidate_cache()

        self.ticket_closed_6 = self.env['helpdesk.ticket'].create({
            'name': 'Ticket 12',
            'user_id': self.user_member_user.id,
            'team_id': self.team_general.id,
            'company_id': company,
            'stage_id': self.stage_fold_true.id,
            })
        self.env.cr.execute("""UPDATE helpdesk_ticket SET create_date = %s WHERE id = %s""", (lastmonth, self.ticket_closed_6.id))
        self.ticket_closed_6.invalidate_cache()

        # Create a Digest Record
        self.digest_record = self.env.ref('digest.digest_digest_default')
        self.digest_record.kpi_helpdesk_ticket_opened = True
        self.digest_record.kpi_helpdesk_ticket_closed = True
        self.kpis_data = self.digest_record.compute_kpis(self.env.company, self.env.user)
