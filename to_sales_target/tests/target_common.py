from odoo.tests.common import SavepointCase, Form


class TargetCommon(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TargetCommon, cls).setUpClass()

        # Create data user
        ResUsers = cls.env['res.users'].with_context({'no_reset_password': True, 'tracking_disable': True})
        cls.user_salesman = ResUsers.create({
            'name': 'User Sale',
            'login': 'user sale',
            'email': 'sales.user@example.viindoo.com',
            'groups_id': [(6, 0, [cls.env.ref('sales_team.group_sale_salesman').id])]
        })

        cls.user_leader = ResUsers.create({
            'name': 'User Team leader',
            'login': 'team leader',
            'email': 'sales.leader@example.viindoo.com',
            'groups_id': [(6, 0, [cls.env.ref('to_sales_team_advanced.group_sale_team_leader').id])]
        })

        cls.user_regional = ResUsers.create({
            'name': 'User Regional Manager',
            'login': 'regional manager',
            'email': 'sales.regional@example.viindoo.com',
            'groups_id': [(6, 0, [cls.env.ref('to_sales_team_advanced.group_sale_regional_manager').id])]
        })

        user_regional2 = ResUsers.create({
            'name': 'User Regional Manager2',
            'login': 'regional manager2',
            'email': 'sales.regional2@example.viindoo.com',
            'groups_id': [(6, 0, [cls.env.ref('to_sales_team_advanced.group_sale_regional_manager').id])]
        })

        cls.user_alldoc = ResUsers.create({
            'name': 'User All Document',
            'login': 'sale all document',
            'email': 'sales.alldoc@example.viindoo.com',
            'groups_id': [(6, 0, [cls.env.ref('sales_team.group_sale_salesman_all_leads').id])]
        })

        # Create data region
        Region = cls.env['crm.team.region']
        cls.region1 = Region.create({
            'name': 'HaiPhong',
            'user_id': cls.user_regional.id
        })

        cls.region2 = Region.create({
            'name': 'DaNang',
            'user_id': user_regional2.id
        })

        # Create data Team
        CrmTeam = cls.env['crm.team']
        cls.team1 = CrmTeam.create({
            'name': 'SaleHP',
            'user_id': cls.user_leader.id,
            'crm_team_region_id': cls.region1.id,
            'member_ids': [(6, 0, [cls.user_salesman.id, cls.user_leader.id])],
        })
        cls.team2 = CrmTeam.create({
            'name': 'SaleDN',
            'crm_team_region_id': cls.region1.id,
            'member_ids': [(6, 0, [cls.user_alldoc.id])],
        })

    @classmethod
    def form_create_team_target(cls, sale_team, start_date, end_date, target=100, user_create=False):
        target_form = Form(cls.env['team.sales.target'].with_user(user_create or cls.env.user))
        target_form.crm_team_id = sale_team
        target_form.start_date = start_date
        target_form.end_date = end_date
        target_form.target = target
        return target_form.save()
