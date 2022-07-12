# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})

    warehouse_ids = env['stock.warehouse'].search([])
    if warehouse_ids:
        warehouse_ids._create_foreign_trade_seq_pktype()

