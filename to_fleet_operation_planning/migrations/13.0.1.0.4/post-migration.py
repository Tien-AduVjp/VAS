from odoo import api, SUPERUSER_ID
from odoo.addons.to_fleet_operation_planning import change_no_update


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    external_ids = ['fleet.fleet_rule_contract_visibility_user', 'fleet.fleet_rule_cost_visibility_user',
                    'fleet.fleet_rule_service_visibility_user', 'fleet.fleet_rule_fuel_log_visibility_user']
    change_no_update(env, external_ids, True)
