# -*- coding: utf-8 -*-

from odoo.tests import tagged
from odoo.addons.project.tests import test_portal
from odoo.tools import mute_logger

@tagged('access_rights')
class TestPortalProject(test_portal.TestPortalProject):

    @mute_logger('odoo.addons.base.models.ir_model')
    def test_portal_project_access_rights(self):
        super(TestPortalProject, self).test_portal_project_access_rights()
