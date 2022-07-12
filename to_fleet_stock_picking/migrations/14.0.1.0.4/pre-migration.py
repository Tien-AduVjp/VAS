from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    cr.execute(
        """
        UPDATE ir_model_data
        SET noupdate = True
        WHERE module = 'to_fleet_stock_picking'
        AND name = 'to_fleet_stock_picking_res_config_settings'
        """
    )
