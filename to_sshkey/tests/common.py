import os
import base64

from odoo.tests import common


class SSHKeyCommon(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(SSHKeyCommon, cls).setUpClass()
        cls.ssh_demo_partner = cls.env['res.partner'].create({
            'name': 'SSH Demo User',
            'company_id': cls.env.ref('base.main_company').id,
            'company_name': 'YourCompany',
            'street': '3575  Buena Vista Avenue',
            })
        cls.ssh_demo_user = cls.env['res.users'].create({
            'partner_id': cls.ssh_demo_partner.id,
            'login': 'ssh_demo_user',
            'password': 'ssh_demo_user',
            'company_id': cls.env.ref('base.main_company').id,
            'groups_id': [(6, 0, [cls.env.ref('base.group_user').id])]
            })
        cls.ssh_demo_partner2 = cls.env['res.partner'].create({
            'name': 'SSH Demo User2',
            'company_id': cls.env.ref('base.main_company').id,
            'company_name': 'YourCompany',
            'street': '3575  Buena Vista Avenue',
            })
        cls.ssh_demo_user2 = cls.env['res.users'].create({
            'partner_id': cls.ssh_demo_partner2.id,
            'login': 'ssh_demo_user2',
            'password': 'ssh_demo_user2',
            'company_id': cls.env.ref('base.main_company').id,
            'groups_id': [(6, 0, [cls.env.ref('base.group_user').id])]
            })

        cls.sshkey_pair_vals = {
            'name': 'test_id_rsa',
            'priv_key':"""-----BEGIN RSA PRIVATE KEY-----
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
-----END RSA PRIVATE KEY-----
""",
            'pub_key': """ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDGVmiA1oZFSOBHo3h9K8bzK3t5bn1pR8WYB2y/EFrtUWcD8xmsfmFf6xCrpcQyC4jEXPCL5TJ+ycRpkkqV68o4fhPz74m+jwlF/kKuFSSf3M6s55qMosjjRc2xxQ+XDSWCV/q4tkPhtDB58bjZwSiy4JVKrrI1H4Aiovg8XEabiRLx+4WKSeSUCDwazwsmcb1LioWkB787GXTGe3vsBnfp31cTLktsCtIS3JQvye30gZuXR2QAaHNRnR8Xrfkv4so+WSVeCS7uqqbsN2L3yuocERsdRyWkkG1IhpCKS6bYnZ8ywF36gCjiryiI/z/hRvE19uJvNhRryxVxR1lTzxlTg76U3iyl1wntfWy/3QhipqYTuOqsP8u00z36TRtxD5xjsXWiqbmFtRL1CXRtuJ3WDxqoDOi9jF7QZqWtr2Wm0Ze6N3U/wjtowusr1RRDyTWhPOVEF5IAuZA5d+fDAqQ8tyxd08qvRpIlu72tYfNFNkagRVHu4B/nGzOF+SQrpLiaFanhhN/qxQ2BmufmLMFcLEKaUfvYRsbfA06ZZTqTM/ohjNS2dAO4+8HZ7YCMQUH0KluMTiXwJW1eSU1SKxEz4De6YpMJN++7NhTxTTdEhy67RfN/+vZm2P4au1SGOA1Wvn0hRyNH1JyfZXcZtm7LWHcSTL9o2fpl/c7V/0NenQ== test@viindoo.com
""",
            'privkey_passphrare': False,
            'type': 'rsa',
            'pubkey_fingerprint': '20:19:72:19:80:a3:cc:21:3b:bb:2a:86:d9:21:4f:0d',
            }
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sshkeys/test_id_rsa'), 'rb') as f:
            cls.sshkey_pair_vals['priv_key_bytes'] = f.read()
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sshkeys/test_id_rsa.pub'), 'rb') as f:
            cls.sshkey_pair_vals['pub_key_bytes'] = f.read()

        cls.passworded_sshkey_pair_vals = {
            'name': 'test_passwd_id_rsa',
            'privkey_passphrare': '123456',
            'type': 'rsa',
            }
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sshkeys/test_id_rsa_with_passwd'), 'rb') as f:
            cls.passworded_sshkey_pair_vals['priv_key_bytes'] = f.read()
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sshkeys/test_id_rsa_with_passwd.pub'), 'rb') as f:
            cls.passworded_sshkey_pair_vals['pub_key_bytes'] = f.read()

        # invalid SSH Key which was generated with OpenSSH without `-m PEM` option
        cls.invalid_sshkey_pair_vals = {
            'name': 'test_invalid_id_rsa',
            'privkey_passphrare': False,
            'type': 'rsa',
            }
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sshkeys/test_invalid_id_rsa'), 'rb') as f:
            cls.invalid_sshkey_pair_vals['priv_key_bytes'] = f.read()
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sshkeys/test_invalid_id_rsa.pub'), 'rb') as f:
            cls.invalid_sshkey_pair_vals['pub_key_bytes'] = f.read()

    @classmethod
    def create_sshkey_pair(cls, sshkey_vals, user=None, company=None):
        return cls.env['sshkey.pair'].create({
            'name': cls.sshkey_pair_vals['name'],
            'type': sshkey_vals['type'],
            'privkey_bin': base64.b64encode(sshkey_vals['priv_key_bytes']),
            'privkey_filename': sshkey_vals['name'],
            'pubkey_bin': base64.b64encode(sshkey_vals['pub_key_bytes']),
            'pubkey_filename': '%s.pub' % sshkey_vals['name'],
            'privkey_passphrare': sshkey_vals['privkey_passphrare'],
            'user_id': user and user.id or False,
            'company_id': company and company.id or False,
            })
