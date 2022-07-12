from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    """ Allow internal users to access Quality menu and see their own assigned checks """
    env = api.Environment(cr, SUPERUSER_ID, {})
    env.ref('to_quality.quality_root_menu').write({
        'groups_id': [(3, env.ref('to_quality.group_quality_user').id)]
        })
