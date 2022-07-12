from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    all_lead_ids = env['crm.lead'].with_context(active_test=False).search([])
    team_ids = all_lead_ids.mapped('team_id')
    for team_id in team_ids:
        all_lead_ids.filtered(lambda l: l.team_id == team_id).write({
            'team_leader_id': team_id.user_id and team_id.user_id.id or False,
            'regional_manager_id': team_id.regional_manager_id and team_id.regional_manager_id.id or False,
            'crm_team_region_id': team_id.crm_team_region_id and team_id.crm_team_region_id.id or False
            })
