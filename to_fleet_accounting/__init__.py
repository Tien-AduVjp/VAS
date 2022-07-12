from . import models
from . import report
from . import wizard

from odoo import api, SUPERUSER_ID


def _generate_products(env):
    service_types = env['fleet.service.type'].search([])
    service_types._generate_product_if_not_exists()
    vechile_costs = env['fleet.vehicle.cost'].search([('cost_subtype_id', 'in', service_types.ids)])
    for c in vechile_costs:
        c.product_id = c.cost_subtype_id.product_id


def _update_vendors(env):
    env['fleet.vehicle.log.services'].update_vendors()
    env['fleet.vehicle.log.fuel'].update_vendors()
    env['fleet.vehicle.log.contract'].update_vendors()


def _generate_analytic_accounts_for_vehicles(env):
    all_vehicles = env['fleet.vehicle'].with_context(active_test=False).search([])
    all_vehicles._generate_analytic_account_if_not_exists()


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _generate_products(env)
    _update_vendors(env)
    _generate_analytic_accounts_for_vehicles(env)

