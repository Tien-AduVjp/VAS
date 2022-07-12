from odoo.tests.common import TransactionCase, Form

class Common(TransactionCase):
    def setUp(self):
        super(Common, self).setUp()

        self.department_management = self.env.ref('hr.dep_management')
        self.department_research_development = self.env.ref('hr.dep_rd')

        # Create data user
        ResUsers = self.env['res.users'].with_context({'no_reset_password': True, 'tracking_disable': True})
        # User with full accounting feature
        self.user_full_accounting_feature = ResUsers.create({
            'name': 'User Full Accounting Feature',
            'login': 'user_full_accounting_feature',
            'email': 'user.full.accounting.feature@example.viindoo.com',
            'groups_id': [(6, 0, [self.env.ref('account.group_account_user').id, self.env.ref('analytic.group_analytic_accounting').id, self.env.ref('analytic.group_analytic_tags').id])],
        })

        # User with analytic accounting
        self.user_analytic_accounting = ResUsers.create({
            'name': 'User Analytic Accounting',
            'login': 'user_analytic_accounting',
            'email': 'user.analytic.accounting@example.viindoo.com',
            'groups_id': [(6, 0, [self.env.ref('account.group_account_user').id, self.env.ref('analytic.group_analytic_accounting').id])],
        })

        # User with analytic accounting tags
        self.user_analytic_accounting_tags = ResUsers.create({
            'name': 'User Analytic Accounting Tags',
            'login': 'user_analytic_accounting_tags',
            'email': 'user.analytic.accounting.tags@example.viindoo.com',
            'groups_id': [(6, 0, [self.env.ref('account.group_account_user').id, self.env.ref('analytic.group_analytic_tags').id])],
        })

    def create_hr_department(self, department_name):
        department_form = Form(self.env['hr.department'])
        department_form.name = department_name
        return department_form.save()

    def create_analytic_tag(self, departments):
        analytic_tag_form = Form(self.env['account.analytic.tag'])
        analytic_tag_form.name = 'Analytic Tag Test'
        analytic_tag_form.active_analytic_distribution = True

        for department in departments:
            analytic_tag_form.department_ids.add(department)

        return analytic_tag_form.save()
