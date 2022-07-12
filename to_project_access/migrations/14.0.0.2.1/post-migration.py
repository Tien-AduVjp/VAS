from odoo import api, SUPERUSER_ID

from odoo.addons.to_project_access import _project_task_visibility_rule


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _project_task_visibility_rule(env)
