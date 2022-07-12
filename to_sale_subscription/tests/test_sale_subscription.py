import odoo.tests


@odoo.tests.tagged('post_install', '-at_install')
class TestSubscription(odoo.tests.HttpCase):

    def test_tour(self):
        self.phantom_js("/web",
                        "odoo.__DEBUG__.services['web_tour.tour'].run('to_sale_subscription_tour')",
                        "odoo.__DEBUG__.services['web_tour.tour'].tours.to_sale_subscription_tour.ready",
                        login="admin")

        #check result
        subscription_template = self.env['sale.subscription.template'].search([('name', '=', 'ERPOnline Monthly ### TOUR DATA ###')])
        self.assertTrue(subscription_template, 'Not found subscription template!')

        product_template = self.env['product.template'].search([('name', '=', 'ERPOnline SAAS Monthly ### TOUR DATA ###')])
        self.assertTrue(product_template, 'Not found subscription product!')
        self.assertTrue(product_template.recurring_invoice, 'Subscription products option is not activated!')
        self.assertEqual(product_template.subscription_template_id, subscription_template)
