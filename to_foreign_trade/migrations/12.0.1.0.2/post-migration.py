# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})

    warehouse_ids = env['stock.warehouse'].search([])
    if warehouse_ids:
        for warehouse in warehouse_ids:       
            if warehouse.import_to_resupply:
                res = warehouse._create_foreign_routes()  
                warehouse.write(res)      
                if warehouse.delivery_steps != 'ship_only':
                    if warehouse.foreign_mto_pull_id:
                        warehouse.foreign_mto_pull_id.active = False
                else:
                    warehouse.foreign_mto_pull_id = warehouse._create_mto_export_pull_rule().id         

