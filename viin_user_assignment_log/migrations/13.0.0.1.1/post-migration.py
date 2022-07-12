from odoo import api, SUPERUSER_ID


def _remove_junk_data(env):
    assignments = env['user.assignment'].search([])
    assignments.filtered(lambda a: a.res_model not in env).unlink()


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _remove_junk_data(env)
