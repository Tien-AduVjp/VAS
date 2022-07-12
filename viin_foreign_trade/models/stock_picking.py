from odoo import fields, models, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    is_custom_clearance = fields.Boolean(string="Is Clearance Location?",
                                         related='location_dest_id.is_custom_clearance',
                                         readonly=True,
                                         help='Indicate if the destination location is a custom clearance zone')
    custom_declaration_import_ids = fields.Many2many('custom.declaration.import',
                                                    groups='viin_foreign_trade.group_foreign_trade_user,stock.group_stock_user',
                                                    string="Custom Clearance Import Request", readonly=True)
    custom_declaration_export_ids = fields.Many2many('custom.declaration.export',
                                                    groups='viin_foreign_trade.group_foreign_trade_user,stock.group_stock_user',
                                                    string="Custom Clearance Export Request", readonly=True)

    custom_dec_import_count = fields.Integer(string="# of Custom Clearance Import Request",
                                             groups='viin_foreign_trade.group_foreign_trade_user,stock.group_stock_user',
                                             compute='_compute_custom_dec_import_count', compute_sudo=True)
    custom_dec_export_count = fields.Integer(string="# of Custom Clearance Export Request",
                                             groups='viin_foreign_trade.group_foreign_trade_user,stock.group_stock_user',
                                             compute='_compute_custom_dec_export_count', compute_sudo=True)
    custom_dec_required = fields.Boolean(string='Custom Declaration Required', compute='_compute_custom_dec_required', store=True)

    def _compute_custom_dec_import_count(self):
        for r in self:
            r.custom_dec_import_count = len(r.custom_declaration_import_ids)

        # custom_dec_data = self.env['custom.declaration.import'].sudo().read_group([('stock_picking_id', 'in', self.ids)], ['stock_picking_id'], ['stock_picking_id'])
        # mapped_data = dict([(dict_data['stock_picking_id'][0], dict_data['stock_picking_id_count']) for dict_data in custom_dec_data])
        # for r in self:
        #     r.custom_dec_import_count = mapped_data.get(r.id, 0)

    def _compute_custom_dec_export_count(self):
        for r in self:
            r.custom_dec_export_count = len(r.custom_declaration_export_ids)

        # custom_dec_data = self.env['custom.declaration.export'].sudo().read_group([('stock_picking_id', 'in', self.ids)], ['stock_picking_id'], ['stock_picking_id'])
        # mapped_data = dict([(dict_data['stock_picking_id'][0], dict_data['stock_picking_id_count']) for dict_data in custom_dec_data])
        # for r in self:
        #     r.custom_dec_export_count = mapped_data.get(r.id, 0)

    @api.depends('custom_declaration_import_ids', 'custom_declaration_export_ids', 'location_dest_id.is_custom_clearance')
    def _compute_custom_dec_required(self):
        for r in self:
            custom_dec_count = r.custom_dec_import_count + r.custom_dec_export_count
            if custom_dec_count == 0 and r.location_dest_id.is_custom_clearance:
                r.custom_dec_required = True
            else:
                r.custom_dec_required = False
