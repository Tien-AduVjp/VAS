from odoo.tests.common import SavepointCase


class TestCommon(SavepointCase):
    
    def setUp(self):
        super(TestCommon, self).setUp()
        
        self.git_repo1 = self.env['git.repository'].create({
            'remote_url': 'remote url test',
            'name': 'repository1 test'
        })
        
        self.git_branch1 = self.env['git.branch'].with_context(skip_check_branch_name=True).create({
            'name': 'branch1',
            'repository_id': self.git_repo1.id,
        })
        self.git_branch14 = self.env['git.branch'].with_context(skip_check_branch_name=True).create({
            'name': '14.1.1',
            'repository_id': self.git_repo1.id
        })
        self.git_branch15 = self.env['git.branch'].with_context(skip_check_branch_name=True).create({
            'name': 'git branch 15',
            'repository_id': self.git_repo1.id
        })
        
        self.odoo_version13 = self.env['odoo.version'].create({
            'name': '13.1.1',
            'release_date': '2021-09-25'
        })
        self.odoo_version15 = self.env['odoo.version'].create({
            'name': '15.0.1',
            'release_date': '2021-09-25'
        })
