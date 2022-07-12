from . import models
from odoo import api, SUPERUSER_ID


####### POST INIT HOOK #######
def _show_project_menu_to_internal_users(env):
    env.ref('project.menu_main_pm').write({
        'groups_id': [(4, env.ref('base.group_user').id)]
        })

    
def _project_public_members_rule(env):
    env.ref('project.project_public_members_rule').write({
        'perm_write': False,
        'perm_create': False,
        'perm_unlink': False
        })


####### UNINSTALL HOOK #######
def _hide_project_menu_from_internal_users(env):
    env.ref('project.menu_main_pm').write({
        'groups_id': [(3, env.ref('base.group_user').id)]
        })


def _revert_project_public_members_rule(env):
    env.ref('project.project_public_members_rule').write({
        'perm_write': True,
        'perm_create': True,
        'perm_unlink': True
        })


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _show_project_menu_to_internal_users(env)
    _project_public_members_rule(env)


def uninstall_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _revert_project_public_members_rule(env)
    _hide_project_menu_from_internal_users(env)
