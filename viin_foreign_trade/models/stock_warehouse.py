from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    import_to_resupply = fields.Boolean(string='Enable Foreign Import/Export',
                                        help="When products are imported from oversea, they can be delivered to this warehouse")
    buy_import_pull_id = fields.Many2one('stock.rule', 'Foreign Import rule')

    foreign_mto_pull_id = fields.Many2one('stock.rule', 'Foreign MTO rule')

    imp_custom_zone_loc_id = fields.Many2one('stock.location',
                                           string='Import - Custom Location',
                                           help='The location where the incoming goods must be stopped for custom clearance')

    exp_custom_zone_loc_id = fields.Many2one('stock.location',
                                           string='Export - Custom Location',
                                           help='The location where the outgoing goods must be stopped for custom clearance')

    imp_type_id = fields.Many2one('stock.picking.type',
                                          string='Foreign Import Type')

    exp_type_id = fields.Many2one('stock.picking.type',
                                          string='Foreign Export Type')

    imp_custom_zone_type_id = fields.Many2one('stock.picking.type',
                                          string='Import Custom Clearance')

    exp_custom_zone_type_id = fields.Many2one('stock.picking.type',
                                          string='Export Custom Clearance')

    import_route_id = fields.Many2one('stock.location.route', string='Import Route')
    export_route_id = fields.Many2one('stock.location.route', string='Export Route')

    def _get_imex_sequence_values(self):
        seq_vals = {
            'imp_seq_id': {'name': self.name + _(' Sequence Import'), 'prefix': self.code + '/IMP/', 'padding': 5, 'company_id': self.company_id.id},
            'imp_receipt_seq_id': {'name': self.name + _(' Sequence Import - Receipt'), 'prefix': self.code + '/IMP-IN/', 'padding': 5, 'company_id': self.company_id.id},
            'exp_seq_id': {'name': self.name + _(' Sequence Export'), 'prefix': self.code + '/EXP/', 'padding': 5, 'company_id': self.company_id.id},
            'exp_out_seq_id': {'name': self.name + _(' Sequence Export - Ship'), 'prefix': self.code + '/EXP-Out/', 'padding': 5, 'company_id': self.company_id.id}
            }
        return seq_vals

    @api.model
    def _create_sequence_if_not_exists(self, data, ir_sequence_model=None):
        """
        @param data_to_check: {'name': self.name + _(' Sequence Import'), 'prefix': self.code + '/IMP/', 'padding': 5, 'company_id': self.company_id.id}
        @type dict:
        @return: ir.sequence record
        @rtype: ir.sequence
        """
        IrSequenceSudo = ir_sequence_model or self.env['ir.sequence'].sudo()
        sequence_id = IrSequenceSudo.search([
            ('name', 'ilike', data['name']),
            ('company_id', '=', data['company_id'])], limit=1)
        if not sequence_id:
            sequence_id = IrSequenceSudo.create(data)
        return sequence_id

    def _create_foreign_trade_seq_pktype(self):
        """
        This method will create, if not exists, all the necessary sequences and picking types and locations for the warehouse to serve import/export operations
        """
        IrSequenceSudo = self.env['ir.sequence'].with_context(active_test=False).sudo()
        StockLocation = self.env['stock.location'].with_context(active_test=False)
        PickingType = self.env['stock.picking.type'].with_context(active_test=False)
        for r in self:
            imp_custom_zone_loc_id = StockLocation.search([
                ('name', 'ilike', _('Import - Custom Zone')),
                ('location_id', '=', r.view_location_id.id)], limit=1)
            if not imp_custom_zone_loc_id:
                imp_custom_zone_loc_id = StockLocation.create({
                    'name': _('Import - Custom Zone'),
                    'active': r.import_to_resupply,
                    'is_custom_clearance': True,
                    'usage': 'internal',
                    'location_id': r.view_location_id.id,
                    'company_id': r.company_id.id,
                    })
            else:
                imp_custom_zone_loc_id.write({'active': r.import_to_resupply, 'is_custom_clearance': True})

            exp_custom_zone_loc_id = StockLocation.search([
                ('name', 'ilike', _('Export - Custom Zone')),
                ('location_id', '=', r.view_location_id.id)], limit=1)
            if not exp_custom_zone_loc_id:
                exp_custom_zone_loc_id = StockLocation.create({
                    'name': _('Export - Custom Zone'),
                    'active': r.import_to_resupply,
                    'is_custom_clearance': True,
                    'usage': 'internal',
                    'location_id': r.view_location_id.id,
                    'company_id': r.company_id.id,
                    })
            else:
                exp_custom_zone_loc_id.write({'active': r.import_to_resupply, 'is_custom_clearance': True})

            sequence_data = r._get_imex_sequence_values()

            imp_seq_id = r._create_sequence_if_not_exists(sequence_data['imp_seq_id'], IrSequenceSudo)
            imp_receipt_seq_id = r._create_sequence_if_not_exists(sequence_data['imp_receipt_seq_id'], IrSequenceSudo)
            exp_seq_id = r._create_sequence_if_not_exists(sequence_data['exp_seq_id'], IrSequenceSudo)
            exp_out_seq_id = r._create_sequence_if_not_exists(sequence_data['exp_out_seq_id'], IrSequenceSudo)

            wh_stock_loc = r.lot_stock_id
            wh_input_stock_loc = r.wh_input_stock_loc_id
            wh_output_stock_loc = r.wh_output_stock_loc_id

            # create in, out, internal picking types for warehouse
            input_loc = wh_input_stock_loc
            if r.reception_steps == 'one_step':
                input_loc = wh_stock_loc
            output_loc = wh_output_stock_loc
            if r.delivery_steps == 'ship_only':
                output_loc = wh_stock_loc

            # choose the next available color for the picking types of this warehouse
            all_used_colors = [res['color'] for res in PickingType.search_read([('warehouse_id', '!=', False), ('color', '!=', False)], ['color'], order='color')]
            available_colors = [zef for zef in [0, 3, 4, 5, 6, 7, 8, 1, 2] if zef not in all_used_colors]
            color = available_colors and available_colors[0] or 0

            # order the picking types with a sequence allowing to have the following suit for each warehouse: reception, internal, pick, pack, ship.
            max_sequence = r.env['stock.picking.type'].search_read([], ['sequence'], order='sequence desc')
            max_sequence = max_sequence and max_sequence[0]['sequence'] or 0

            imp_type_id = PickingType.search([
                ('name', 'ilike', _('Import - Custom Zone')),
                ('warehouse_id', '=', r.id),
                ('code', '=', 'incoming'),
                ('default_location_dest_id', '=', imp_custom_zone_loc_id.id)], limit=1)
            if not imp_type_id:
                imp_type_id = PickingType.create({
                    'name': _('Import - Custom Zone'),
                    'warehouse_id': r.id,
                    'code': 'incoming',
                    'sequence_code': 'IN',
                    'is_foreign_trade': True,
                    'use_create_lots': True,
                    'use_existing_lots': False,
                    'sequence_id': imp_receipt_seq_id.id,
                    'default_location_src_id': False,
                    'default_location_dest_id': imp_custom_zone_loc_id.id,
                    'custom_clearance_type': 'import',
                    'sequence': max_sequence + 1,
                    'color': color,
                    'active': r.import_to_resupply,
                    'company_id': r.company_id.id,
                    })
            else:
                imp_type_id.write({'active': r.import_to_resupply, 'is_foreign_trade':True, 'custom_clearance_type': 'import'})

            imp_custom_zone_type_id = PickingType.search([
                ('name', 'ilike', _('Import - Receipt')),
                ('warehouse_id', '=', r.id),
                ('code', '=', 'internal'),
                ('default_location_src_id', '=', imp_custom_zone_loc_id.id),
                ('default_location_dest_id', '=', input_loc.id)], limit=1)
            if not imp_custom_zone_type_id:
                imp_custom_zone_type_id = PickingType.create({
                    'name': _('Import - Receipt'),
                    'warehouse_id': r.id,
                    'sequence_code': 'INT',
                    'code': 'internal',
                    'use_create_lots': True,
                    'use_existing_lots': False,
                    'sequence_id': imp_seq_id.id,
                    'default_location_src_id': imp_custom_zone_loc_id.id,
                    'default_location_dest_id': input_loc.id,
                    'sequence': max_sequence + 1,
                    'color': color,
                    'active': r.import_to_resupply,
                    'company_id': r.company_id.id,
                    })
            else:
                imp_custom_zone_type_id.write({'active': r.import_to_resupply})

            exp_custom_zone_type_id = PickingType.search([
                ('name', 'ilike', _('Export - Custom Zone')),
                ('warehouse_id', '=', r.id),
                ('code', '=', 'internal'),
                ('default_location_src_id', '=', output_loc.id),
                ('default_location_dest_id', '=', exp_custom_zone_loc_id.id)], limit=1)
            if not exp_custom_zone_type_id:
                exp_custom_zone_type_id = PickingType.create({
                    'name': _('Export - Custom Zone'),
                    'warehouse_id': r.id,
                    'sequence_code': 'INT',
                    'code': 'internal',
                    'use_create_lots': False,
                    'use_existing_lots': True,
                    'sequence_id': exp_out_seq_id.id,
                    'default_location_src_id': output_loc.id,
                    'default_location_dest_id': exp_custom_zone_loc_id.id,
                    'active': r.import_to_resupply,
                    'custom_clearance_type': 'export',
                    'sequence': max_sequence + 2,
                    'color': color,
                    'company_id': r.company_id.id,
                    })
            else:
                exp_custom_zone_type_id.write({'active': r.import_to_resupply, 'custom_clearance_type': 'export', })

            foreign_customer_loc = self.env.ref('viin_foreign_trade.to_stock_location_customers_export')
            exp_type_id = PickingType.search([
                ('name', 'ilike', _('Export - Delivery')),
                ('warehouse_id', '=', r.id),
                ('code', '=', 'outgoing'),
                ('default_location_src_id', '=', exp_custom_zone_loc_id.id)], limit=1)
            if not exp_type_id:
                exp_type_id = PickingType.create({
                    'name': _('Export - Delivery'),
                    'warehouse_id': r.id,
                    'sequence_code': 'OUT',
                    'code': 'outgoing',
                    'use_create_lots': False,
                    'use_existing_lots': True,
                    'sequence_id': exp_seq_id.id,
                    'default_location_src_id': exp_custom_zone_loc_id.id,
                    'default_location_dest_id': foreign_customer_loc.id,
                    'active': r.import_to_resupply,
                    'sequence': max_sequence + 2,
                    'color': color,
                    'company_id': r.company_id.id,
                    })
            else:
                exp_type_id.write({'active': r.import_to_resupply, 'default_location_dest_id': foreign_customer_loc.id})

            r.write({
                'imp_custom_zone_loc_id':imp_custom_zone_loc_id.id,
                'exp_custom_zone_loc_id': exp_custom_zone_loc_id.id,
                'exp_custom_zone_type_id': exp_custom_zone_type_id.id,
                'exp_type_id': exp_type_id.id,
                'imp_custom_zone_type_id': imp_custom_zone_type_id.id,
                'imp_type_id': imp_type_id.id,
                })

    @api.model
    def update_existing_warehouses(self):
        for warehouse in self.search([]):
            warehouse._create_foreign_trade_seq_pktype()
            # create routes
            if warehouse.import_to_resupply:
                res = warehouse._create_foreign_routes()
                warehouse.write(res)
        warehouse0 = self.env.ref('stock.warehouse0')
        if warehouse0:
            warehouse0.write({'import_to_resupply': True})

    def _get_buy_import_pull_rule(self):
        buy_import_route_id = self.env.ref('viin_foreign_trade.route_warehouse0_import')
        return {
            'name': self._format_routename(_('Buy - Foreign Import')),
            'location_id': self.imp_type_id.default_location_dest_id.id,
            'route_id': buy_import_route_id.id,
            'action': 'buy',
            'picking_type_id': self.imp_type_id.id,
            'warehouse_id': self.id,
            'group_propagation_option': 'none',
        }

    def _get_foreign_mto_pull_rule(self):
        if not self.exp_custom_zone_loc_id:
            raise ValidationError(_('Export Custom Zone/Location has not been set for warehouse %s') % (self))
        mto_route_id = self.env.ref('stock.route_warehouse0_mto')
        return {
            'name': self._format_rulename(self.lot_stock_id, self.exp_custom_zone_loc_id, _(' MTO')),
            'location_src_id': self.lot_stock_id.id,
            'location_id': self.exp_custom_zone_loc_id.id,
            'route_id': mto_route_id.id,
            'action': 'pull',
            'active': True,
            'picking_type_id': self.exp_custom_zone_type_id.id,
            'procure_method': 'make_to_order',
            'warehouse_id': self.id,
        }

    def _prepare_import_route_data(self):
        return {
            'name': self._format_routename(_('Importing - Receipt')),
            'sequence': 9,
            'product_selectable': False,
            'product_categ_selectable': True,
            'warehouse_ids': [(4, self.id)]
            }

    def _get_input_loc(self):
        """
        Method to get input location, which is either lot_stock_id or wh_input_stock_loc_id, depending on the reception steps
        """
        if self.reception_steps == 'one_step':
            input_loc = self.lot_stock_id
        else:
            input_loc = self.wh_input_stock_loc_id
        return input_loc

    @api.model
    def _prepare_import_stock_rules_data(self, import_route=None, name_suffix=''):
        import_route = import_route or self.import_route_id
        input_loc = self._get_input_loc()

        data = {
            'name': self._format_rulename(self.imp_custom_zone_loc_id, input_loc, name_suffix),
            'location_src_id': self.imp_custom_zone_loc_id.id,
            'location_id': input_loc.id,
            'route_id': import_route.id,
            'action': 'pull_push',
            'auto': 'manual',
            'active': True,
            'procure_method': 'make_to_order',
            'picking_type_id': self.imp_custom_zone_type_id.id,
            'warehouse_id': self.id,
            'group_propagation_option': 'propagate',
            'delay': 5,
        }
        return data

    @api.model
    def _prepare_import_push_rules_data(self, import_route=None, name_suffix=''):
        import_route = import_route or self.import_route_id
        input_loc = self._get_input_loc()
        data = {
            'name': self._format_rulename(self.imp_custom_zone_loc_id, input_loc, name_suffix),
            'location_from_id': self.imp_custom_zone_loc_id.id,
            'location_dest_id': input_loc.id,
            'route_id': import_route.id,
            'auto': 'manual',
            'active': True,
            'picking_type_id': self.imp_custom_zone_type_id.id,
            'warehouse_id': self.id,
            'delay': 5,
        }
        return data

    def _prepare_export_route_data(self):
        return {
            'name': self._format_routename(_('Exporting - Ship')),
            'sequence': 11,
            'product_selectable': False,
            'product_categ_selectable': True,
            'warehouse_ids': [(4, self.id)]
            }

    @api.model
    def _create_foreign_routes(self):
        res = {}
        if not self.buy_import_pull_id:
            res['buy_import_pull_id'] = self._create_buy_import_pull_rule().id
        else:
            res['buy_import_pull_id'] = self.buy_import_pull_id.id

        if not self.foreign_mto_pull_id and self.delivery_steps == 'ship_only':
            res['foreign_mto_pull_id'] = self._create_mto_export_pull_rule().id
        else:
            res['foreign_mto_pull_id'] = self.foreign_mto_pull_id.id

        StockLocationRoute = self.env['stock.location.route']

        # create import route and its push and pull rules
        import_route_id = self.import_route_id
        if not import_route_id:
            import_route_data = self._prepare_import_route_data()
            import_route_id = StockLocationRoute.search([('name', 'ilike', import_route_data['name']), ('warehouse_ids', 'in', self.id)], limit=1)
        if not import_route_id:
            import_route_id = StockLocationRoute.create(import_route_data)
        res['import_route_id'] = import_route_id.id
        self._create_import_push_pull_rules(import_route_id)

        # create export route and its push and pull rules
        export_route_id = self.export_route_id
        if not export_route_id:
            export_route_data = self._prepare_export_route_data()
            export_route_id = StockLocationRoute.search([('name', 'ilike', export_route_data['name']), ('warehouse_ids', 'in', self.id)], limit=1)
        if not export_route_id:
            export_route_id = StockLocationRoute.create(export_route_data)
        res['export_route_id'] = export_route_id.id
        self._create_export_pull_rules(export_route_id)

        return res

    def _create_import_push_pull_rules(self, import_route_id=None):
        """
        Create import stock rules if not exists
        """
        StockRule = self.env['stock.rule']
        import_route = import_route_id or self.import_route_id
        pull_rule_id = StockRule.with_context(active_test=False).search([
            ('location_src_id', '=', self.imp_custom_zone_loc_id.id),
#            ('location_id', '=', input_loc.id),
            ('route_id', '=', import_route.id),
            ('picking_type_id', '=', self.imp_custom_zone_type_id.id),
            ('warehouse_id', '=', self.id)], limit=1)

        stock_rule_data = self._prepare_import_stock_rules_data(import_route_id)
        if not pull_rule_id:
            StockRule.create(stock_rule_data)
        else:
            pull_rule_id.write(stock_rule_data)

    def _create_export_pull_rules(self, export_route_id=None):

        StockRule = self.env['stock.rule']
        export_route = export_route_id or self.export_route_id
        if not export_route:
            raise ValidationError(_('Cannot find any export route'))
        if not self.exp_custom_zone_loc_id:
            raise ValidationError(_('Export Custom Zone/Location has not been set for warehouse %s') % (self))

        for rule in export_route.rule_ids:
            rule.active = False

        foreign_customer_loc = self.env.ref('viin_foreign_trade.to_stock_location_customers_export')
        output_loc = self.delivery_steps == 'ship_only' and self.lot_stock_id or self.wh_output_stock_loc_id
        pull_rule = {
            'name': self._format_rulename(self.exp_custom_zone_loc_id, foreign_customer_loc, ''),
            'location_src_id': self.exp_custom_zone_loc_id.id,
            'location_id': foreign_customer_loc.id,
            'route_id': export_route.id,
            'action': 'pull',
            'active': True,
            'procure_method': 'make_to_order',
            'picking_type_id': self.exp_type_id.id,
            'warehouse_id': self.id,
            'group_propagation_option': 'propagate',
        }
        pull_rule_id = StockRule.with_context(active_test=False).search([
            ('location_src_id', '=', pull_rule['location_src_id']),
            ('location_id', '=', pull_rule['location_id']),
            ('route_id', '=', pull_rule['route_id']),
            ('action', '=', pull_rule['action']),
            ('procure_method', '=', pull_rule['procure_method']),
            ('picking_type_id', '=', pull_rule['picking_type_id']),
            ('warehouse_id', '=', pull_rule['warehouse_id'])], limit=1)
        if not pull_rule_id:
            StockRule.create(pull_rule)
        else:
            pull_rule_id.write(pull_rule)
        pull_rule = {
            'name': self._format_rulename(output_loc, self.exp_custom_zone_loc_id, ''),
            'location_src_id': output_loc.id,
            'location_id': self.exp_custom_zone_loc_id.id,
            'route_id': export_route.id,
            'action': 'pull',
            'active': True,
            'procure_method': self.delivery_steps == 'ship_only' and 'make_to_stock' or 'make_to_order',
            'picking_type_id': self.exp_custom_zone_type_id.id,
            'warehouse_id': self.id,
            'group_propagation_option': 'propagate',
        }
        pull_rule_id = StockRule.with_context(active_test=False).search([
            ('location_id', '=', pull_rule['location_id']),
            ('route_id', '=', pull_rule['route_id']),
            ('action', '=', pull_rule['action']),
            ('picking_type_id', '=', pull_rule['picking_type_id']),
            ('warehouse_id', '=', pull_rule['warehouse_id'])], limit=1)
        if not pull_rule_id:
            StockRule.create(pull_rule)
        else:
            pull_rule_id.write(pull_rule)

    def _create_buy_import_pull_rule(self):
        self.ensure_one()
        StockRule = self.env['stock.rule']
        buy_import_pull_vals = self._get_buy_import_pull_rule()
        import_pull_rule_id = StockRule.with_context(active_test=False).search([
            ('location_id', '=', buy_import_pull_vals['location_id']),
            ('route_id', '=', buy_import_pull_vals['route_id']),
            ('action', '=', buy_import_pull_vals['action']),
            ('picking_type_id', '=', buy_import_pull_vals['picking_type_id']),
            ('warehouse_id', '=', buy_import_pull_vals['warehouse_id'])], limit=1)
        if not import_pull_rule_id:
            pull_rule_id = StockRule.create(buy_import_pull_vals)
        else:
            pull_rule_id.write(buy_import_pull_vals)
        return pull_rule_id

    def _create_mto_export_pull_rule(self):
        self.ensure_one()
        StockRule = self.env['stock.rule']
        foreign_mto_pull_vals = self._get_foreign_mto_pull_rule()
        pull_rule_id = StockRule.with_context(active_test=False).search([
            ('location_src_id', '=', foreign_mto_pull_vals['location_src_id']),
            ('location_id', '=', foreign_mto_pull_vals['location_id']),
            ('route_id', '=', foreign_mto_pull_vals['route_id']),
            ('action', '=', foreign_mto_pull_vals['action']),
            ('procure_method', '=', foreign_mto_pull_vals['procure_method']),
            ('picking_type_id', '=', foreign_mto_pull_vals['picking_type_id']),
            ('warehouse_id', '=', foreign_mto_pull_vals['warehouse_id'])], limit=1)
        if not pull_rule_id:
            pull_rule_id = StockRule.create(foreign_mto_pull_vals)
        else:
            pull_rule_id.write(foreign_mto_pull_vals)
        return pull_rule_id

    def write(self, vals):
        for r in self:
            last_import_to_resupply = r.import_to_resupply
            if 'import_to_resupply' in vals:
                if vals.get('import_to_resupply'):
                    if not r.buy_import_pull_id and 'buy_import_pull_id' not in vals:
                        vals['buy_import_pull_id'] = r._create_buy_import_pull_rule().id
                    if not r.foreign_mto_pull_id and 'foreign_mto_pull_id' not in vals and r.delivery_steps == 'ship_only':
                        vals['foreign_mto_pull_id'] = r._create_mto_export_pull_rule().id
                    r.switch_foreign_trade(True)

                else:
                    if r.buy_import_pull_id:
                        r.buy_import_pull_id.active = False
                    if r.foreign_mto_pull_id:
                        r.foreign_mto_pull_id.active = False
                    # disable foreign related locations and picking types
                    r.switch_foreign_trade(False)
            super(StockWarehouse, r).write(vals)
            if r.import_to_resupply:
                if not r.imp_type_id or not r.exp_type_id:
                    r._create_foreign_trade_seq_pktype()
                update_vals = r._create_foreign_routes()
                super(StockWarehouse, r).write(update_vals)

            reception_step_change = ('reception_steps' in vals) and True or False
            delivery_step_change = ('delivery_steps' in vals) and True or False

            import_to_resupply_change = (last_import_to_resupply != r.import_to_resupply)

            r._change_imex_rules(reception_step_change, delivery_step_change, import_to_resupply_change)
            # _update_routes() is not used from Odoo 13, so we need call _change_foreign_picking_types() from write
            r._change_foreign_picking_types(reception_step_change, delivery_step_change)

        return True

    def _change_imex_rules(self, reception_step_change=False, delivery_step_change=False, import_to_resupply_change=False):

        if import_to_resupply_change or reception_step_change:
            self.import_route_id.rule_ids.write({'active':self.import_to_resupply})

            if self.import_to_resupply:
                self._create_import_push_pull_rules(self.import_route_id)

        if import_to_resupply_change or delivery_step_change:
            self.export_route_id.rule_ids.write({'active':self.import_to_resupply})
            if self.import_to_resupply:
                self._create_export_pull_rules(self.export_route_id)
            if self.import_to_resupply and self.delivery_steps == 'ship_only':
                self.foreign_mto_pull_id = self._create_mto_export_pull_rule().id
            else:
                if self.foreign_mto_pull_id:
                    self.foreign_mto_pull_id.active = False

    def switch_foreign_trade(self, switch):
        self = self.with_context(active_test=False)
        (self.mapped('imp_custom_zone_loc_id') + self.mapped('exp_custom_zone_loc_id')).write({'active': switch})
        (self.mapped('imp_type_id') + self.mapped('exp_type_id') + self.mapped('imp_custom_zone_type_id') + self.mapped('exp_custom_zone_type_id')).filtered(lambda pkt: pkt.count_picking_ready <= 0).write({'active': switch})
        (self.mapped('import_route_id') + self.mapped('export_route_id')).write({'active': switch})

    def _update_name_and_code(self, new_name=False, new_code=False):
        res = super(StockWarehouse, self)._update_name_and_code(new_name, new_code)
        for r in self:
            if r.buy_import_pull_id:
                # FIXME: it's better to re-generate the route naming instead of replacing?
                if new_name:
                    r.buy_import_pull_id.write({'name': r.buy_import_pull_id.name.replace(r.name, new_name, 1)})
        return res

    def _update_location_reception(self, new_reception_step):
        super(StockWarehouse, self)._update_location_reception(new_reception_step)
        buy_import_warehouses = self.filtered(lambda wh: wh.buy_import_pull_id)
        buy_import_warehouses.mapped('imp_custom_zone_loc_id').write({'active': True})
        (self - buy_import_warehouses).mapped('imp_custom_zone_loc_id').write({'active': False})

    def _update_location_delivery(self, new_delivery_step):
        super(StockWarehouse, self)._update_location_delivery(new_delivery_step)

    @api.returns('self')
    def _get_all_routes(self):
        routes = super(StockWarehouse, self)._get_all_routes()
        routes |= self.mapped('buy_import_pull_id.route_id')
        return routes

    def _change_foreign_picking_types(self, reception_step_change=False, delivery_step_change=False):
        if reception_step_change:
            if self.reception_steps == 'one_step':
                input_loc = self.lot_stock_id
            else:
                input_loc = self.wh_input_stock_loc_id
            self.imp_custom_zone_type_id.write({'default_location_dest_id': input_loc.id})

        if delivery_step_change:
            if self.delivery_steps == 'ship_only':
                output_loc = self.lot_stock_id
            else:
                output_loc = self.wh_output_stock_loc_id
            self.exp_custom_zone_type_id.write({'default_location_src_id': output_loc.id})

    def unlink(self):
        self = self.with_context(active_test=False)
        for r in self:
            r.buy_import_pull_id.unlink()
            r.foreign_mto_pull_id.unlink()
            r.import_route_id.unlink()
            r.export_route_id.unlink()
            r.imp_type_id.unlink()
            r.exp_type_id.unlink()
            r.imp_custom_zone_type_id.unlink()
            r.exp_custom_zone_type_id.unlink()
            r.imp_custom_zone_loc_id.unlink()
            r.exp_custom_zone_loc_id.unlink()

        res = super(StockWarehouse, self).unlink()
        return res

    @api.model_create_multi
    def create(self, vals_list):
        warehouse_ids = super(StockWarehouse, self).create(vals_list)
        warehouse_ids._create_foreign_trade_seq_pktype()
        return warehouse_ids
