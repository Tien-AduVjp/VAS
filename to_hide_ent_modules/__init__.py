from odoo import api, SUPERUSER_ID


def uninstall_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})

    open_module_tree_action_id = env.ref('base.open_module_tree', raise_if_not_found=False)
    if open_module_tree_action_id:
        open_module_tree_action_id.write({
            'domain':False
            })

