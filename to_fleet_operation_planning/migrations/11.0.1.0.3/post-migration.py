from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    all_vehicle_ids = env['fleet.vehicle'].with_context(active_test=False).search([])
    all_vehicle_ids.migrate_location_to_address()

