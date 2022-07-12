from odoo import models
from odoo.tests import tagged
from .common import SSHKeyCommon

from ..exceptions import InvalidInput


@tagged('post_install', '-at_install')
class TestSSHKeypair(SSHKeyCommon):

    def test_01_sshkey_wrong_password(self):
        vals = self.passworded_sshkey_pair_vals.copy()
        # set invalid password
        vals['privkey_passphrare'] = '0000000'
        with self.assertRaises(InvalidInput) as e:
            self.create_sshkey_pair(vals, self.ssh_demo_user, self.ssh_demo_user.company_id)

    def test_02_sshkey_right_password(self):
        # create sshkey with the right password
        sshkey_pair = self.create_sshkey_pair(self.passworded_sshkey_pair_vals, self.ssh_demo_user, self.ssh_demo_user.company_id)
        self.assertTrue(isinstance(sshkey_pair, models.Model) and isinstance(sshkey_pair.id, int) and sshkey_pair.id > 0)

    def test_04_personal_sshkey(self):
        sshkey_pair = self.create_sshkey_pair(self.sshkey_pair_vals, self.ssh_demo_user, self.ssh_demo_user.company_id)
        self.assertRecordValues(sshkey_pair, [
            {
                'pubkey_fingerprint': self.sshkey_pair_vals['pubkey_fingerprint'],
                'user_id': self.ssh_demo_user.id,
                'company_id': self.ssh_demo_user.company_id.id,
            }
        ])
        self.assertEqual(sshkey_pair.get_privkey_content(), self.sshkey_pair_vals['priv_key'])
        self.assertEqual(sshkey_pair.get_pubkey_content(), self.sshkey_pair_vals['pub_key'])
        self.assertTrue(sshkey_pair in self.ssh_demo_user.with_user(self.ssh_demo_user).get_available_sshkey_pairs())
        self.assertFalse(
            sshkey_pair in self.ssh_demo_user2.with_user(self.ssh_demo_user2).get_available_sshkey_pairs(),
            "The SSH Key %s should not be accessible by the user %s" % (sshkey_pair.display_name, self.ssh_demo_user2.name)
            )
        self.assertTrue(sshkey_pair in self.env.ref('base.user_root').get_available_sshkey_pairs())
        self.assertTrue(sshkey_pair in self.env.ref('base.user_admin').get_available_sshkey_pairs())

    def test_05_company_sshkey_non_key_user(self):
        sshkey_pair = self.create_sshkey_pair(self.sshkey_pair_vals, company=self.env.ref('base.main_company'))
        self.assertTrue(sshkey_pair in self.ssh_demo_user.with_user(self.ssh_demo_user).get_available_sshkey_pairs())
        self.assertTrue(sshkey_pair in self.ssh_demo_user2.with_user(self.ssh_demo_user2).get_available_sshkey_pairs())
        self.assertTrue(sshkey_pair in self.env.ref('base.user_root').with_user(self.env.ref('base.user_root')).get_available_sshkey_pairs())
        self.assertTrue(sshkey_pair in self.env.ref('base.user_admin').with_user(self.env.ref('base.user_admin')).get_available_sshkey_pairs())

    def test_06_company_sshkey_admin_key_user(self):
        sshkey_pair = self.create_sshkey_pair(self.sshkey_pair_vals, user=self.env.ref('base.user_admin'), company=self.env.ref('base.main_company'))
        self.assertTrue(sshkey_pair not in self.ssh_demo_user.with_user(self.ssh_demo_user).get_available_sshkey_pairs())
        self.assertTrue(sshkey_pair not in self.ssh_demo_user2.with_user(self.ssh_demo_user2).get_available_sshkey_pairs())
        self.assertTrue(sshkey_pair in self.env.ref('base.user_root').with_user(self.env.ref('base.user_root')).get_available_sshkey_pairs())
        self.assertTrue(sshkey_pair in self.env.ref('base.user_admin').with_user(self.env.ref('base.user_admin')).get_available_sshkey_pairs())

    def test_07_use_current_company_sshkey(self):
        no_name_company = self.env['res.company'].create({
            'name': 'No Name Company',
        })
        user_root = self.env.ref('base.user_root')
        user_admin = self.env.ref('base.user_admin')
        user_admin.write({
            'company_ids': [(4, no_name_company.id)]
        })
        sshkey_pair = self.create_sshkey_pair(self.sshkey_pair_vals, company=no_name_company)
        self.assertTrue(sshkey_pair not in user_root.with_user(user_root).get_available_sshkey_pairs())
        self.assertTrue(sshkey_pair not in user_admin.with_user(user_admin).get_available_sshkey_pairs())

        self.env.company = no_name_company
        user_admin = user_admin.with_company(no_name_company)
        self.assertTrue(sshkey_pair in user_admin.with_user(user_admin).get_available_sshkey_pairs())
        self.assertTrue(sshkey_pair in user_root.with_user(user_root).get_available_sshkey_pairs())
