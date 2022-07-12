from odoo.tests.common import TransactionCase

class Common(TransactionCase):
    def setUp(self):
        super(Common, self).setUp()
        
        self.ownership_type_joint_stock_company = self.env['res.partner.ownership.type'].create({
                'name': 'Joint Stock Company'
        })
        
        self.contact_a = self.env['res.partner'].create({
            'name':'Contact A',
            'company_type': 'company',
            'ownership_type_id': self.ownership_type_joint_stock_company.id
        })
        
        self.contact_b = self.env['res.partner'].create({
            'name':'Contact B',
            'company_type': 'person'
        })

        #Create users
        self.user_partner_manager = self.env.ref('base.user_admin')
        self.user_internal = self.env['res.users'].with_context(tracking_disable=True).create({
            'name': 'Internal User',
            'login': 'internal_user',
            'email': 'user@example.viindoo.com',
            'groups_id': [(6, 0, [self.env.ref('base.group_user').id])],
        })
