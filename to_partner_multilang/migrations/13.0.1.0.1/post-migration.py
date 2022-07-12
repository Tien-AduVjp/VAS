from odoo import api, fields, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})

    # Update the translations of display_name and commercial_company_name fields of records
    trans = env['ir.translation'].search([('name', '=', 'res.partner,name')])
    trans._update_translations_of_res_partner()
