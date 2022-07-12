from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    cr.execute(
        """
        UPDATE ir_model_data
        SET noupdate = True
        WHERE module = 'to_pos_delivery'
        AND name = 'stock_config_settings_pos_delivery'
        """
    )
