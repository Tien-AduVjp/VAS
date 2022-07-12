from odoo.tests.common import SavepointCase, Form


class TestCommon(SavepointCase):

    def setUp(self):
        super(TestCommon, self).setUp()
        self.account_type = self.env['account.account.type'].create({
            'name': 'SKRT',
            'internal_group': 'asset',
            'type': 'receivable'
        })
        self.journal_test = self.env['account.journal'].create({
            'name': 'LAMBDA',
            'code': 'L',
            'type': 'bank',
        })
        self.account_test = self.env['account.account'].create({
            'name': 'Account Test',
            'code': '111333',
            'user_type_id': self.account_type.id,
            'reconcile': True,
        })

    def _create_payment(self, payment_type):
        form = Form(self.env['account.payment'])
        form.payment_type = payment_type
        form.partner_type = 'customer'
        form.partner_id = self.env.ref('base.res_partner_12')
        form.amount = 50000
        form.journal_id = self.journal_test
        with form.account_payment_line_ids.new() as line:
            line.name = 'Label 01'
            line.account_id = self.account_test
            line.amount = 30000
        with form.account_payment_line_ids.new() as line:
            line.name = 'Label 02'
            line.account_id = self.account_test
            line.amount = 5000
        return form.save()
