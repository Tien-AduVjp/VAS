# -*- coding: utf-8 -*-
import os

from odoo.exceptions import UserError
from odoo.tests import tagged

from . import common


@tagged('post_install', '-at_install')
class TestGitRepo(common.TestGitCommon):

    def test_checkout_private_repo_with_valid_sshkey(self):
        self.create_sshkey_pair(self.sshkey_pair_vals, company=self.env.ref('base.main_company'))
        self.private_repo.scan_for_branches()
        url_parse_data = self.env['git.branch'].parse_git_url(self.private_repo.remote_url)
        repo_path = os.path.join(self.git_data_path, str(self.private_repo.id), 'repo')
        self.assertTrue(len(self.private_repo.branch_ids) > 0)
        self.assertEqual(self.private_repo.netloc,
                         'git@github.com',
                         "net location of private repository should be `git@github.com`, not `%s`" % url_parse_data.netloc)
        self.assertEqual(self.private_repo.domain_name,
                         'github.com',
                         "domain name of private repository should be `github.com`, not `%s`" % url_parse_data.netloc.split('@')[-1])
        self.assertEqual(self.private_repo.netpath,
                         '/Viindoo/test_private.git',
                         "net path of private repository should be `/Viindoo/test_private.git`, not `%s`" % url_parse_data.path)
        self.assertEqual(self.private_repo.scheme,
                         'ssh',
                         "scheme of private repository should be `ssh`, not `%s`" % url_parse_data.scheme)
        self.assertEqual(self.private_repo.path,
                         repo_path,
                         "private repository path should be `%s`" % repo_path)
        self.private_repo.branch_ids.checkout()
        self.assertTrue(all(branch.checked_out for branch in self.private_repo.branch_ids))
        self.private_repo.branch_ids.un_checkout()

    def test_checkout_private_repo_without_valid_sshkey(self):
        with self.assertRaises(UserError) as e:
            self.private_repo.scan_for_branches()
        self.assertIn('Permission denied (publickey)', str(e.exception))

    def test_checkout_public_repo(self):
        self.public_repo.scan_for_branches()
        url_parse_data = self.env['git.branch'].parse_git_url(self.public_repo.remote_url)
        repo_path = os.path.join(self.git_data_path, str(self.public_repo.id), 'repo')
        self.assertTrue(len(self.public_repo.branch_ids) > 0)
        self.assertEqual(self.public_repo.netloc,
                         'github.com',
                         "net location of private repository should be `github.com`, not `%s`" % url_parse_data.netloc)
        self.assertEqual(self.public_repo.domain_name,
                         'github.com',
                         "domain name of private repository should be `github.com`, not `%s`" % url_parse_data.netloc.split('@')[-1])
        self.assertEqual(self.public_repo.netpath,
                         '/Viindoo/test_public.git',
                         "net path of private repository should be `/Viindoo/test_public.git`, not `%s`" % url_parse_data.path)
        self.assertEqual(self.public_repo.scheme,
                         'https',
                         "scheme of private repository should be `https`, not `%s`" % url_parse_data.scheme)
        self.assertEqual(self.public_repo.path,
                         repo_path,
                         "private repository path should be `%s`" % repo_path)
        self.public_repo.branch_ids.checkout()
        self.assertTrue(all(branch.checked_out for branch in self.public_repo.branch_ids))
        self.public_repo.branch_ids.un_checkout()
