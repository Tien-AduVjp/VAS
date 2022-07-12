from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    cr.execute("""
        ALTER TABLE res_partner DROP CONSTRAINT IF EXISTS res_partner_vat_uniq;
    """)
