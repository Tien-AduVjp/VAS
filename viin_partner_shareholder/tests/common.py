from odoo.tests.common import TransactionCase

class Common(TransactionCase):
    def setUp(self):
        super(Common, self).setUp()

        self.contact_a = self.env['res.partner'].with_context(tracking_disable=True).create({
            'name':'Contact A',
            'is_company': True,
        })

        self.contact_b = self.env['res.partner'].with_context(tracking_disable=True).create({
            'name':'Contact B',
            'is_company': True,
        })

        self.share_holder_1 = self.env['res.partner.shareholder'].create({
            'partner_id' : self.contact_a.id,
            'shareholder_id': self.env.ref('base.res_partner_address_15').id,
            'ownership_rate': 12,
        })

        self.share_holder_2 = self.env['res.partner.shareholder'].create({
            'partner_id' : self.contact_b.id,
            'shareholder_id': self.env.ref('base.res_partner_address_15').id,
            'ownership_rate': 12,
        })
        #Create users
        self.user_partner_manager = self.env.ref('base.user_admin')
        self.user_internal = self.env['res.users'].with_context(tracking_disable=True).create({
            'name': 'Internal User',
            'login': 'internal_user',
            'email': 'user@example.viindoo.com',
            'groups_id': [(6, 0, [self.env.ref('base.group_user').id])],
        })
