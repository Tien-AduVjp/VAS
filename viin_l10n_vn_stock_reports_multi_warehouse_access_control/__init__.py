from odoo import api, SUPERUSER_ID


def _rollback_menu_data(env):
    menus = env.ref('to_l10n_vn_stock_reports.menu_l10n_vn_stock_legal_reports')\
            | env.ref('to_l10n_vn_stock_reports.menu_wizard_c200_s10dn')\
            | env.ref('to_l10n_vn_stock_reports.menu_wizard_c200_s11dn')\
            | env.ref('to_l10n_vn_stock_reports.menu_wizard_c200_s12dn')\
            | env.ref('to_l10n_vn_stock_reports.menu_wizard_stock_in')\
            | env.ref('to_l10n_vn_stock_reports.menu_wizard_stock_out')

    menus.write({
        'groups_id': [(3, env.ref('to_multi_warehouse_access_control.group_warehouse_manager').id)],
        })

def uninstall_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _rollback_menu_data(env)
