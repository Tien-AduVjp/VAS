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


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    all_vehicle_ids = env['fleet.vehicle'].with_context(active_test=False).search([])
    all_vehicle_ids.migrate_location_to_address()
