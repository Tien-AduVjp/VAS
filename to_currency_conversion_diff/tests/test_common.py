from odoo.tests import SavepointCase

class TestCommon(SavepointCase):
    
    @classmethod
    def setUpClass(cls):
        super(TestCommon, cls).setUpClass()
        
        # Setup user
        Users = cls.env['res.users'].with_context(no_reset_password=True)
        # Create a users
        cls.user_user = Users.create({
            'name': 'Account User',
            'login': 'user1',
            'email': 'user1@example.viindoo.com',
            'groups_id': [(6, 0, [cls.env.ref('account.group_account_user').id])]
        })
        cls.user_invoice = Users.create({
            'name': 'Account Invoice',
            'login': 'user2',
            'email': 'user2@example.viindoo.com',
            'groups_id': [(6, 0, [cls.env.ref('account.group_account_invoice').id])]
        })
        cls.user_manager = Users.create({
            'name': 'Account Manager',
            'login': 'manager',
            'email': 'manager@example.viindoo.com',
            'groups_id': [(6, 0, [cls.env.ref('account.group_account_manager').id])]
        })
        
        # Create and active currency
        cls.currency_eur = cls.env.ref('base.EUR')
        cls.currency_usd = cls.env.ref('base.USD')
        cls.currency_vnd = cls.env.ref('base.VND')
        cls.currency_jpy = cls.env.ref('base.JPY')
        cls.currency_hkd = cls.env.ref('base.HKD')
        cls.currency_fkp = cls.env.ref('base.FKP')
        cls.currency_eur.active = True
        cls.currency_usd.active = True
        cls.currency_vnd.active = True
        cls.currency_jpy.active = True
        cls.currency_hkd.active = True
        
        cls.default_payment_acquirer = cls.env.ref('payment.payment_acquirer_transfer')
        
        # Setup default supported currency for payment.payment_acquirer_transfer
        # Setup default converted currency for payment.payment_acquirer_transfer
        cls.default_payment_acquirer.write({
            'supported_currency_map_ids': [
                (0, 0, {
                    'currency_id': cls.currency_eur.id,
                }),
                (0, 0, {
                    'currency_id': cls.currency_usd.id,
                })
            ],
            'default_converted_currency_id': cls.currency_usd.id
        })
