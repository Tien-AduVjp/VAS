from odoo import api, SUPERUSER_ID


def migrate(cr, installed_version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    uom_user_day_record = env.ref('to_uom_subscription.uom_subscription_odoo_user_day', raise_if_not_found=False)
    if uom_user_day_record:
        env['ir.model.data']._update_xmlids([{'xml_id': 'to_uom_subscription.uom_subscription_user_day', 'record': uom_user_day_record}])
