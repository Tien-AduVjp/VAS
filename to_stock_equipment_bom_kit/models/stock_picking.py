# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Picking(models.Model):
    _inherit = "stock.picking"

    product_set_line_ids = fields.One2many('product.set', 'picking_id', string='Product Set', groups='stock.group_stock_user')
        
