from . import models
from odoo import api, SUPERUSER_ID


####### POST INIT HOOK #######
def _show_project_menu_to_internal_users(env):
    env.ref('project.menu_main_pm').write({
        'groups_id': [(4, env.ref('base.group_user').id)]
        })


def _project_public_members_rule(env):
    env.ref('project.project_public_members_rule').write({
        'domain_force': """[
        '|', '|',
            ('privacy_visibility', '!=', 'followers'),
            ('allowed_internal_user_ids', 'in', user.ids),
            ('tasks.allowed_user_ids', 'in', user.ids),
        ]""",
        'perm_write': False,
        'perm_create': False,
        'perm_unlink': False
        })


def _project_task_visibility_rule(env):
    env.ref('project.task_visibility_rule').write({
        'domain_force': """[
        '|',
                ('project_id.privacy_visibility', '!=', 'followers'),
                '|',
                    '|',
                        ('project_id.allowed_internal_user_ids', 'in', [user.id]),
                        ('project_id.allowed_portal_user_ids', 'in', [user.id]),
                    '|',
                        ('allowed_user_ids', 'in', [user.id]),
                        # to subscribe check access to the record, follower is not enough at creation
                        ('user_id', '=', user.id)
        ]""",
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
        'domain_force': """[
        '|',
            ('privacy_visibility', '!=', 'followers'),
            ('allowed_internal_user_ids', 'in', user.ids),
        ]""",
        'perm_write': True,
        'perm_create': True,
        'perm_unlink': True
        })


def _revert_project_task_visibility_rule(env):
    env.ref('project.task_visibility_rule').write({
        'domain_force': """[
        '|',
            ('project_id.privacy_visibility', '!=', 'followers'),
            ('allowed_user_ids', 'in', user.ids),
        ]""",
        'perm_write': True,
        'perm_create': True,
        'perm_unlink': True,
        })


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _show_project_menu_to_internal_users(env)
    _project_public_members_rule(env)
    _project_task_visibility_rule(env)


def uninstall_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _revert_project_public_members_rule(env)
    _revert_project_task_visibility_rule(env)
    _hide_project_menu_from_internal_users(env)
