from odoo import fields, models, _


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'


    asset_type_id = fields.Many2one(
        'stock.picking.type', 'Asset Allocation Type',
        domain=[('code', '=', 'asset_allocation')])

    def _get_sequence_values(self):
        values = super(StockWarehouse, self)._get_sequence_values()
        values.update({
            'asset_type_id': {'name': self.name + ' ' + _('Sequence asset allocation'), 
                              'prefix': self.code + '/ASSET/', 'padding': 5,
                              'company_id': self.company_id.id,
                              },
        })
        return values

    def _get_picking_type_create_values(self, max_sequence):
        data, next_sequence = super(StockWarehouse, self)._get_picking_type_create_values(max_sequence)
        data.update({
            'asset_type_id': {
                'name': _('Asset Allocation'),
                'code': 'asset_allocation',
                'use_create_lots': False,
                'use_existing_lots': True,
                'sequence': next_sequence + 2,
                'sequence_code': 'ASSET',
                'company_id': self.company_id.id,
            },
        })
        return data, max_sequence + 4

    def _get_picking_type_update_values(self):
        data = super(StockWarehouse, self)._get_picking_type_update_values()
        data.update({
            'asset_type_id': {
                'active': True,
                'default_location_src_id': self.lot_stock_id.id,
                'default_location_dest_id': self.env.ref('to_stock_asset.stock_location_asset').id,
            },
        })
        return data
