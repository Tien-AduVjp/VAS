from odoo.tests.common import TransactionCase


class Common(TransactionCase):
    
    def setUp(self):
        super(Common, self).setUp()
        self.Account = self.env['account.account'].with_context(tracking_disable=True)
        self.AccountTaxGroup = self.env['account.tax.group'].with_context(tracking_disable=True)
        self.AccountTax = self.env['account.tax'].with_context(tracking_disable=True)
        self.AccountTaxRepartitionLine = self.env['account.tax.repartition.line'].with_context(tracking_disable=True)
        self.user_type_id = self.env.ref('account.data_account_type_liquidity')
        self.account = self.Account.create({
            'code': 'Code 1',
            'name': 'Demo 1',
            'user_type_id': self.user_type_id.id
        })
        self.account_tax_group1 = self.AccountTaxGroup.create({
            'name': 'Demo 1',
            'vat_ctp_account_id': self.account.id,
            'is_vat':True
        })
        self.account_tax_group2 = self.AccountTaxGroup.create({
            'name': 'Demo 2',
            'is_vat':False
        })
        self.account_tax1 = self.AccountTax.create({
            'name': 'Demo Tax 1',
            'tax_group_id': self.account_tax_group1.id,
            'amount': 10
        })
        self.account_tax2 = self.AccountTax.create({
            'name': 'Demo Tax 2',
            'tax_group_id': self.account_tax_group2.id,
            'amount': 10
        })
