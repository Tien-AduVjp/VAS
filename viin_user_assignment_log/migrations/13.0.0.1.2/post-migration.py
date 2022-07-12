from odoo import api, SUPERUSER_ID


def _keep_existing_assignment_track(env):
    models_to_track = env['user.assignment'].search([('res_model', 'not in', ['web_tour.tour', 'bus.presence'])]).mapped('model_id')
    models_to_track.write({'track_user_assignment': True})


def _remove_bus_present_assignment_logs(env):
    env['user.assignment'].search([('res_model', '=', 'bus.presence')]).unlink()


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _keep_existing_assignment_track(env)
    _remove_bus_present_assignment_logs(env)
