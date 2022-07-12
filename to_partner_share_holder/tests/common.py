from odoo.tests.common import TransactionCase, Form

class Common(TransactionCase):
    def setUp(self):
        super(Common, self).setUp()
        
        self.contact_a = self.env['res.partner'].with_context(tracking_disable=True).create({
            'name':'Contact A',
            'company_type': 'company',
        })
        
        self.share_holder = self.env['res.partner.shareholder'].create({
            'partner_id' : self.contact_a.id,
            'shareholder_id': self.env.ref('base.res_partner_12').id,
            'owned_percentage': 12,
            'description': 'test share holder'
        })

        #Create users
        self.user_partner_manager = self.env.ref('base.user_admin')
        self.user_internal = self.env['res.users'].with_context(tracking_disable=True).create({
            'name': 'Internal User',
            'login': 'internal_user',
            'email': 'user@example.viindoo.com',
            'groups_id': [(6, 0, [self.env.ref('base.group_user').id])],
        })
