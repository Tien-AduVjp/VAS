from odoo.tests.common import TransactionCase

class Common(TransactionCase):
    def setUp(self):
        super(Common, self).setUp()
        
        self.equity_range_5_10M_USD = self.env['res.partner.equity.range'].create({
            'name': 'From 5 to 10M USD'
        })
        
        self.contact_a = self.env.ref('base.res_partner_12')
        self.contact_a.equity_range_id = self.equity_range_5_10M_USD.id
        
        self.contact_b = self.env.ref('base.res_partner_address_31')
        
        #Create users
        self.user_partner_manager = self.env.ref('base.user_admin')
        
        self.user_internal = self.env.ref('base.user_demo')
        self.user_internal.write({
            'groups_id': [(6, 0, [self.env.ref('base.group_user').id])]
        })
