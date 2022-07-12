from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    versions = env.ref('to_odoo_version.odoo_v14') + env.ref('to_odoo_version.odoo_v15')
    osv_memory_age_limit_config = versions.config_ids.filtered(
        lambda c: c.name == 'osv_memory_age_limit'
    )
    osv_memory_age_limit_config.write({'name': 'transient_age_limit'})
