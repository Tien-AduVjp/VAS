from odoo import fields, models, api

class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    is_foreign_trade = fields.Boolean(string='Foreign Trade',
                                      help='If check, this will be used dedicatedly for foreign trade')

    custom_clearance_type = fields.Selection([
        ('import', 'Import'),
        ('export', 'Export')
    ], string="Custom Clearance Type")

    is_custom_clearance = fields.Boolean(string="Is Clearance Location?",
                                         related='default_location_dest_id.is_custom_clearance',
                                         readonly=True, store=True, index=True)

    custom_authority_id = fields.Many2one('res.partner', string='Custom Authority', compute='_compute_custom_authority_id',
                                          help='The custom authority serving this operaton type', store=True, index=True)


    @api.depends('custom_clearance_type', 'default_location_dest_id.custom_authority_id')
    def _compute_custom_authority_id(self):
        for r in self:
            if r.custom_clearance_type:
                r.custom_authority_id = r.default_location_dest_id.custom_authority_id
            else:
                r.custom_authority_id = False


    @api.onchange('code')
    def onchange_picking_code(self):
        if self.code not in ['incoming','outgoing']:
            self.is_foreign_trade = False


    @api.model
    def _update_default_location(self):
        wh_id = self.env['ir.model.data'].xmlid_to_res_id('stock.warehouse0', raise_if_not_found=False)
        if wh_id:
            wh = self.env['stock.warehouse'].browse(wh_id)
            return self._update_location(wh)
        return True

    @api.model
    def _update_location(self, warehouse, new_reception_step=False, new_delivery_step=False):
        import_vals = {}
        export_vals = {}
        new_reception_step = new_reception_step or warehouse.reception_steps
        new_delivery_step = new_delivery_step or warehouse.delivery_steps

        if new_reception_step == 'one_step':
            import_vals = {'default_location_dest_id': warehouse.lot_stock_id and warehouse.lot_stock_id.id or False}
        else:
            import_vals = {'default_location_dest_id': warehouse.wh_input_stock_loc_id and warehouse.wh_input_stock_loc_id.id or False}

        if new_delivery_step == 'ship_only':
            export_vals = {'default_location_src_id': warehouse.lot_stock_id and warehouse.lot_stock_id.id or False}
        else:
            export_vals = {'default_location_src_id': warehouse.wh_output_stock_loc_id and warehouse.wh_output_stock_loc_id.id or False}

        # update dest location of nhap kho hang nhap
        import_in_id = self.env['ir.model.data'].xmlid_to_res_id('viin_foreign_trade.to_stock_picking_type_import_in', raise_if_not_found=False)
        if import_in_id and import_vals:
            import_in = self.env['stock.picking.type'].browse(import_in_id)
            import_in.write(import_vals)

        # update src location of xuat kho hang nhap
        export_in_id = self.env['ir.model.data'].xmlid_to_res_id('viin_foreign_trade.to_stock_picking_type_export_out', raise_if_not_found=False)
        if export_in_id and export_vals:
            export_in = self.env['stock.picking.type'].browse(export_in_id)
            export_in.write(export_vals)

        return True
