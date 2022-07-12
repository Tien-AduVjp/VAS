from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    trip_rule = env.ref('to_fleet_operation_planning.fleet_rule_trip_visibility_fleet_operator', raise_if_not_found=False)
    if trip_rule:
        fleet_user = env.ref('fleet.fleet_group_user')
        trip_rule.write({'groups': [(3, fleet_user.id, 0)]})
