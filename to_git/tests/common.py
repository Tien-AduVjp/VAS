# -*- coding: utf-8 -*-
import os
from odoo.tools import config
from odoo.addons.to_sshkey.tests.common import SSHKeyCommon


class TestGitCommon(SSHKeyCommon):

    @classmethod
    def setUpClass(cls):
        super(TestGitCommon, cls).setUpClass()
        data_path = config.filestore(cls.cr.dbname)
        cls.git_data_path = os.path.join(data_path, 'git')
        cls.public_repo = cls.env['git.repository'].create({
            'remote_url': 'https://github.com/Viindoo/test_public.git',
            'name': 'test_public',
            })
        cls.private_repo = cls.env['git.repository'].create({
            'remote_url': 'git@github.com:Viindoo/test_private.git',
            'name': 'test_private',
            })
