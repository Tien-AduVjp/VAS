from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    """ Fix type_id in quality_alert """
    env = api.Environment(cr, SUPERUSER_ID, {})
    env.cr.execute("""
        UPDATE quality_alert qa
        SET type_id = qc.type_id
        FROM quality_check qc
        WHERE qa.check_id = qc.id
            AND qa.check_id IS NOT NULL
    """)
