from odoo import api, SUPERUSER_ID


def _remove_implied_groups(env):
    group_account_user = env.ref('account.group_account_user', raise_if_not_found=False)
    group_product_price_access = env.ref('to_product_standard_price_access.group_product_price_access', raise_if_not_found=False)
    if group_account_user and group_product_price_access and group_account_user.implied_ids.filtered(lambda r: r == group_product_price_access):
        group_account_user.write({
            'implied_ids': [(3, group_product_price_access.id, 0)]
        })

def uninstall_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _remove_implied_groups(env)
