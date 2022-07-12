from . import models, wizard, report
from odoo import api, SUPERUSER_ID


def change_no_update(env, external_ids=[], noupdate=True):
    xml_ids = []
    for external_id in external_ids:
        xml = env.ref(external_id, raise_if_not_found=False)
        if xml:
            xml_ids.append(xml.id)
    domain = [('model', '=', 'ir.rule'), ('res_id', 'in', xml_ids)]
    env['ir.model.data'].search(domain).write({'noupdate': noupdate})

def revert_fleet_group_manager(env):
    env.ref('fleet.fleet_group_manager').write({
        'name': 'Administrator',
        'implied_ids': [
            (3, env.ref('to_fleet_operation_planning.fleet_group_operator').id, 0),
            (3, env.ref('to_geo_routes.group_manager').id, 0)
        ],
        'category_id': env.ref('base.module_category_human_resources_fleet').id,
    })

def revert_fleet_rule_vehicle_visibility_user(env):
    env.ref('fleet.fleet_rule_vehicle_visibility_user').write({
        'name': 'User can only see his/her vehicle',
        'domain_force': "[('driver_id','=',user.partner_id.id)]",
    })

def revert_fleet_rule_service_visibility_user(env):
    env.ref('fleet.fleet_rule_service_visibility_user').write({
        'domain_force': "[('cost_id.vehicle_id.driver_id','=',user.partner_id.id)]",
    })

def revert_fleet_rule_odometer_visibility_user(env):
    env.ref('fleet.fleet_rule_odometer_visibility_user').write({
        'domain_force': "[('vehicle_id.driver_id','=',user.partner_id.id)]",
    })

def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    all_vehicle_ids = env['fleet.vehicle'].with_context(active_test=False).search([])
    all_vehicle_ids.migrate_location_to_address()

def uninstall_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    # Revert security rules
    revert_fleet_group_manager(env)
    revert_fleet_rule_vehicle_visibility_user(env)
    revert_fleet_rule_service_visibility_user(env)
    revert_fleet_rule_odometer_visibility_user(env)
