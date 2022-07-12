from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    """ Unlink old res.config.settings view to avoid error on upgrading """
    env = api.Environment(cr, SUPERUSER_ID, {})
    old_view = env.ref('to_mrp_mps.view_mrp_config_form_inherit_mrp_mps', raise_if_not_found=False)
    if old_view:
        old_view.unlink()
