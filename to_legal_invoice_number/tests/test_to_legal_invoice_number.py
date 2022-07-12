from odoo.tests import TransactionCase, tagged
from odoo.exceptions import AccessError


@tagged('post_install', '-at_install')
class TestLegalInvoiceNumber(TransactionCase):

    def setUp(self):
        super(TestLegalInvoiceNumber, self).setUp()
        self.invoice = self.env['account.move'].create({'move_type': 'out_invoice'})
        self.user_accountant = self.env['res.users'].create({
            'name': 'user_accountant',
            'login': 'user_accountant@example.viindoo.com',
            'email': 'user_accountant@example.viindoo.com',
            'groups_id': [(6, 0, self.env.ref('account.group_account_user').ids)],
        })
        self.user_account_admin = self.env['res.users'].create({
            'name': 'user_account_admin',
            'login': 'user_account_admin@example.viindoo.com',
            'email': 'user_account_admin@example.viindoo.com',
            'groups_id': [(6, 0, self.env.ref('account.group_account_manager').ids)],
        })

    def test_sync_legal_number_access_right(self):
        with self.assertRaises(AccessError):
            self.invoice.with_user(self.user_accountant).action_synch_legal_number()

    def test_sync_legal_number_vs_invoice_name(self):
        invoice_name = self.invoice.name
        self.invoice.legal_number = '00001'
        self.invoice.with_user(self.user_account_admin).action_synch_legal_number()
        self.assertEqual(self.invoice.old_number, invoice_name)
        self.assertEqual(self.invoice.name, '00001')

    def test_sync_legal_number_vs_payment_reference(self):
        self.invoice.legal_number = '00001'
        self.invoice.with_user(self.user_account_admin).action_synch_legal_number()
        self.assertEqual(self.invoice.payment_reference, '00001')
