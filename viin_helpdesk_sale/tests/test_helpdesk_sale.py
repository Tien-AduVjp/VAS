from odoo.tests import tagged, Form, SavepointCase


@tagged('post_install', '-at_install')
class TestHelpdeskSale(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestHelpdeskSale, cls).setUpClass()
        context = dict(cls.env.context, allowed_company_ids=cls.env['res.company'].browse(1).ids)
        cls.env = cls.env(context=context)
        cls.customer_support_team = cls.env['helpdesk.team'].search(
            [('name', '=', 'Customer Support'), ('company_id', '=', cls.env.company.id)], limit=1)
        cls.sale_order = cls.env.ref('sale.sale_order_1')

    def test_onchange_sale_order_01(self):
        # - Change sale_order on ticket form => team change to Customer Support if exists
        form = Form(self.env['helpdesk.ticket'])
        form.sale_order_id = self.sale_order
        self.assertEqual(form.team_id, self.customer_support_team)

    def test_onchange_sale_order_02(self):
        """ Change sale_order on ticket form, Customer Support team does not exists
            => team change to default helpdesk team """
        self.customer_support_team.unlink()
        form = Form(self.env['helpdesk.ticket'])
        form.sale_order_id = self.sale_order
        self.assertEqual(form.team_id, self.env.company.default_helpdesk_team_id)
