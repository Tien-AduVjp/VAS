from odoo.tests import new_test_user
from odoo.tests.common import SavepointCase


class TestActivityPlanningCommon(SavepointCase):

    def setUp(self):
        super(TestActivityPlanningCommon, self).setUp()

        no_mailthread_features_ctx = {
            'no_reset_password': True,
            'tracking_disable': True
            }

        self.hubert_emp = self.env.ref('hr.employee_admin')
        self.richard_emp = self.env.ref('hr.employee_niv')

        self.hubert = new_test_user(self.env,
                                    login='hub',
                                    groups='base.group_user',
                                    name='Simple employee',
                                    email='hub@example.viindoo.com',
                                    context=no_mailthread_features_ctx)

        self.hubert_emp.with_context(no_mailthread_features_ctx).update({
            'name': 'Hubert',
            'user_id': self.hubert.id,
            'address_home_id': self.env['res.partner'].create({
                'name': 'Hubert',
                'type': 'private'
                }).id,
            })
        self.richard = new_test_user(self.env,
                                     login='ric',
                                     groups='base.group_user',
                                     name='Simple employee',
                                     email='ric@example.viindoo.com',
                                     context=no_mailthread_features_ctx)
        self.richard_emp.update({
            'name': 'Richard',
            'user_id': self.richard.id,
            'address_home_id': self.env['res.partner'].create({
                'name': 'Richard',
                'phone': '21454',
                'type': 'private'
                }).id,
            'parent_id': self.hubert_emp.id,
            })

        self.richard_emp_public = self.env['hr.employee.public'].browse(self.richard_emp.id)
        self.onboarding_plan = self.env.ref('hr.onboarding_plan')
        self.message_follower = self.env['mail.followers'].sudo().create([{
            'res_model': 'hr.employee',
            'res_id': self.richard_emp,
            'partner_id': self.richard.partner_id.id
            },
            {'res_model': 'hr.employee',
            'res_id': self.hubert_emp,
            'partner_id': self.hubert.partner_id.id}
            ])

        PlanWizard = self.env['hr.plan.wizard'].with_context(
            active_model=self.richard_emp._name,
            active_id=self.richard_emp.id
            )
        wizard = PlanWizard.create({'plan_id': self.onboarding_plan.id})
        wizard.action_launch()
