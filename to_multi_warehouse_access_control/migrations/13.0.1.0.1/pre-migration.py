from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    cr.execute(
        """
        UPDATE ir_model_data
        SET noupdate = True
        WHERE module = 'to_multi_warehouse_access_control'
        AND name = 'res_config_settings_multi_warehouse_access_control'
        """
    )
