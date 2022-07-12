from . import models
from . import wizard

from odoo import api, SUPERUSER_ID


def _generate_products(env):
    service_types = env['fleet.service.type'].search([])
    service_types._generate_product_if_not_exists()
    vechile_services = env['fleet.vehicle.log.services'].search([('service_type_id', 'in', service_types.ids)])
    for s in vechile_services:
        s.product_id = s.service_type_id.product_id


def _generate_analytic_accounts_for_vehicles(env):
    all_vehicles = env['fleet.vehicle'].with_context(active_test=False).search([])
    all_vehicles._generate_analytic_account_if_not_exists()


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _generate_products(env)
    _generate_analytic_accounts_for_vehicles(env)
