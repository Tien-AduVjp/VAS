from odoo.tests.common import tagged

from .common import Common


@tagged('-at_install', 'post_install', 'access_rights')
class TestAccessRights(Common):
    
    def test_manager_user_access_rights(self):
        # Manager Users can read the country state group
        self.state_group1.with_user(self.user_partner_manager).read()
        # Manager Users can create the country state group
        state_group = self.env['res.state.group'].create({
            'name': 'State Group 2',
            'country_id': self.country1.id,
            'state_ids': [self.country_state1.id]
        })
        # Manager Users can write the country state group
        self.state_group1.with_user(self.user_partner_manager).write({'name': 'State Group Test'})
        # Manager Users can delete the country state group
        state_group.with_user(self.user_partner_manager).unlink()
