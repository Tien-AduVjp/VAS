from collections import defaultdict, namedtuple
from math import log10
from datetime import timedelta
from odoo import api, fields, models, _
from odoo.tools.misc import format_date
from odoo.tools.float_utils import float_round
from odoo.osv import expression


class MrpProductionSchedule(models.Model):
    _name = 'mrp.production.schedule'
    _description = 'MRP Production Schedule'
    _order = 'warehouse_id, sequence'

    @api.model
    def _default_warehouse_id(self):
        return self.env['stock.warehouse'].search([('company_id', '=', self.env.company.id)], limit=1)

    mrp_product_forecast_ids = fields.One2many('mrp.product.forecast', 'production_schedule_id', string='Product Forecast')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    product_tmpl_id = fields.Many2one('product.template', related="product_id.product_tmpl_id")
    product_uom_id = fields.Many2one('uom.uom', string='UoM', related='product_id.uom_id')
    sequence = fields.Integer(related='product_id.sequence', store=True)
    forecast_target_qty = fields.Float('Safety Stock Target', default=0)
    min_to_replenish_qty = fields.Float('Minimum to Replenish', default=0)
    max_to_replenish_qty = fields.Float('Maximum to Replenish', default=100)
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse', required=True, default=lambda self: self._default_warehouse_id())
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    _sql_constraints = [
        ('warehouse_product_ref_uniq', 'unique (warehouse_id, product_id)', 'Product must be unique in a warehouse!'),
    ]

    def action_view_actual_demand_pickings(self, date_str, date_start, date_stop):
        self.ensure_one()
        domain_confirm, domain_done = self._get_stock_move_domain(date_start, date_stop, 'outgoing')
        domain = expression.OR([domain_confirm, domain_done])
        picking_ids = self.env['stock.move'].search(domain).picking_id.ids
        date_start_str = format_date(self.env, fields.Date.from_string(date_start))
        date_stop_str = format_date(self.env, fields.Date.from_string(date_stop))
        return {
            'name': _('Actual Demand %s %s (%s - %s)') % (self.product_id.display_name, date_str, date_start_str, date_stop_str),
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'view_mode': 'list,form',
            'views': [(False, 'list'), (False, 'form')],
            'domain': [('id', 'in', picking_ids)],
            'target': 'current',
        }

    def action_view_actual_replenishment(self, date_str, date_start, date_stop):
        domain_confirm, domain_done = self._get_stock_move_domain(date_start, date_stop, 'incoming')
        move_domain = expression.OR([domain_confirm, domain_done])
        move_ids = self.env['stock.move'].search(move_domain).ids

        rfq_domain = self._get_rfq_domain(date_start, date_stop)
        pol_ids = self.env['purchase.order.line'].search(rfq_domain).ids
        date_start_str = format_date(self.env, fields.Date.from_string(date_start))
        date_stop_str = format_date(self.env, fields.Date.from_string(date_stop))

        action_name = _('Actual Replenishment %s %s (%s - %s)') % (self.product_id.display_name, date_str, date_start_str, date_stop_str)
        return {
            'name': action_name,
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.mps.forecast.details',
            'view_mode': 'form',
            'views': [(False, 'form')],
            'context': {
                'action_name': action_name,
                'default_move_ids': move_ids,
                'default_purchase_order_line_ids': pol_ids,
            },
            'target': 'new',
        }

    def action_replenish(self, based_on_lead_time=False):
        """ Run procurements for schedules in self """
        mps_data = {mps['id']: mps for mps in self.get_mps_view_state()}
        procurements = []
        forecasts_values = []
        forecasts_launched = self.env['mrp.product.forecast']

        Procurement = self.env['procurement.group'].Procurement
        for mps in self:
            data = mps_data[mps.id]
            replenishment_field = 'to_replenish' if based_on_lead_time else 'forced_replenish'

            for forecast in data['mrp_product_forecast_ids']:
                if forecast[replenishment_field]:
                    extra_values = {
                        'date_planned': forecast['date_start'],
                        'warehouse_id': mps.warehouse_id,
                    }
                    procurements.append(Procurement(
                        mps.product_id,
                        forecast['replenish_qty'] - forecast['incoming_qty'],
                        mps.product_uom_id,
                        mps.warehouse_id.lot_stock_id,
                        mps.product_id.name,
                        'MPS',
                        mps.company_id,
                        extra_values
                    ))

                    existing_forecasts = mps.mrp_product_forecast_ids.filtered(
                        lambda p: forecast['date_start'] <= p.date <= forecast['date_stop']
                    )
                    if existing_forecasts:
                        forecasts_launched |= existing_forecasts
                    else:
                        forecasts_values.append(mps._prepare_product_forecast_vals(forecast['date_stop'], procurement_launched=True))

        if procurements:
            self.env['procurement.group'].with_context(skip_lead_time=True).run(procurements)
        if forecasts_launched:
            forecasts_launched.write({'procurement_launched': True})
        if forecasts_values:
            self.env['mrp.product.forecast'].create(forecasts_values)

    @api.model
    def get_mps_view_state_by_domain(self, domain=False):
        """ Get view data for client action """
        schedules = self.env['mrp.production.schedule'].search(domain or [])
        mps_states = schedules.get_mps_view_state()
        display_groups = self.env.company._get_mps_display_groups()
        date_range = self.env.company._get_mps_date_range()
        date_range_str = self._date_range_to_str(date_range)
        return {
            'dates': date_range_str,
            'schedule_states': mps_states,
            'manufacturing_period': self.env.company.manufacturing_period,
            'company_id': self.env.company.id,
            'period': self.env.company.manufacturing_period,
            'groups': display_groups,
        }

    def get_mps_view_state(self):
        company = self.env.company
        date_range = company._get_mps_date_range()

        # Get all impacted schedules, because we need to
        # recompute the quantity to replenish for them too.
        impacted_schedule_ids = self.get_impacted_mps_ids()
        schedules_to_recompute = self.browse(impacted_schedule_ids) | self

        indirect_demand_trees = schedules_to_recompute._get_indirect_demand_tree()

        indirect_demand_ordered = schedules_to_recompute._get_indirect_demand_ordered(indirect_demand_trees)
        indirect_demand_qty = defaultdict(float)
        incoming_qty, incoming_qty_done = self._get_move_qty_data(date_range, 'incoming')
        outgoing_qty, outgoing_qty_done = self._get_move_qty_data(date_range, 'outgoing')

        mps_view_states = schedules_to_recompute._get_base_mps_view_states()
        mps_view_states_by_id = {state['id']: state for state in mps_view_states}

        for mps in indirect_demand_ordered:
            rounding = mps.product_id.uom_id.rounding
            lead_time = mps._get_lead_times()
            state = mps_view_states_by_id[mps['id']]
            indirect_demand_ratio = mps._get_indirect_demand_ratio(indirect_demand_trees, schedules_to_recompute)
            if mps in self:
                state['mrp_product_forecast_ids'] = []

            starting_inventory_qty = mps.product_id.with_context(warehouse=mps.warehouse_id.id).qty_available
            if len(date_range):
                key = (date_range[0], mps.product_id, mps.warehouse_id)
                starting_inventory_qty -= incoming_qty_done.get(key, 0.0)
                starting_inventory_qty += outgoing_qty_done.get(key, 0.0)

            for date_start, date_stop in date_range:
                forecast_vals = {}
                key = ((date_start, date_stop), mps.product_id, mps.warehouse_id)
                if mps in self:
                    forecast_vals['date_start'] = date_start
                    forecast_vals['date_stop'] = date_stop
                    forecast_vals['incoming_qty'] = float_round(incoming_qty.get(key, 0.0) + incoming_qty_done.get(key, 0.0), precision_rounding=rounding)
                    forecast_vals['outgoing_qty'] = float_round(outgoing_qty.get(key, 0.0) + outgoing_qty_done.get(key, 0.0), precision_rounding=rounding)

                existing_forecasts = mps.mrp_product_forecast_ids.filtered(lambda p: date_start <= p.date <= date_stop)
                replenish_qty_updated = False
                if existing_forecasts:
                    forecast_vals['forecast_qty'] = float_round(sum(existing_forecasts.mapped('forecast_qty')), precision_rounding=rounding)
                    forecast_vals['replenish_qty'] = float_round(sum(existing_forecasts.mapped('replenish_qty')), precision_rounding=rounding)
                    replenish_qty_updated = any(f.replenish_qty_updated for f in existing_forecasts)
                else:
                    forecast_vals['forecast_qty'] = 0.0

                forecast_vals['indirect_demand_qty'] = float_round(indirect_demand_qty.get(key, 0.0), precision_rounding=rounding)
                if not replenish_qty_updated:
                    after_forecast_qty = starting_inventory_qty - forecast_vals['forecast_qty'] - forecast_vals['indirect_demand_qty']
                    replenish_qty = mps._get_replenish_qty(after_forecast_qty)
                    forecast_vals['replenish_qty'] = float_round(replenish_qty, precision_rounding=rounding)

                forecast_vals['replenish_qty_updated'] = replenish_qty_updated
                forecast_vals['starting_inventory_qty'] = float_round(starting_inventory_qty, precision_rounding=rounding)
                safety_stock_qty = starting_inventory_qty - forecast_vals['forecast_qty'] - forecast_vals['indirect_demand_qty'] + forecast_vals['replenish_qty']
                forecast_vals['safety_stock_qty'] = float_round(safety_stock_qty, precision_rounding=rounding)

                if mps in self:
                    state['mrp_product_forecast_ids'].append(forecast_vals)
                starting_inventory_qty = forecast_vals['safety_stock_qty']

                for (indirect, ratio) in indirect_demand_ratio:
                    if not forecast_vals['replenish_qty']:
                        continue
                    indirect_date = max(date_start + timedelta(days=lead_time), fields.Date.today())
                    index = -1
                    for i, (start, stop) in enumerate(date_range):
                        if indirect_date <= start or start <= indirect_date <= stop:
                            index = i
                            break
                    if index >= 0:
                        indirect_key = (date_range[index], indirect.product_id, indirect.warehouse_id)
                        indirect_demand_qty[indirect_key] += ratio * forecast_vals['replenish_qty']

            if mps in self:
                procurement_date = fields.Date.today() + timedelta(days=lead_time)
                precision_digits = max(0, int(-(log10(mps.product_uom_id.rounding))))
                state['precision_digits'] = precision_digits
                forecasts_state = mps._get_forecasts_state(mps_view_states_by_id, date_range, procurement_date)
                forecasts_state = forecasts_state[mps.id]
                for index, forecast_state in enumerate(forecasts_state):
                    state['mrp_product_forecast_ids'][index].update(forecast_state)

                has_indirect_demand = any(forecast['indirect_demand_qty'] != 0 for forecast in state['mrp_product_forecast_ids'])
                state['has_indirect_demand'] = has_indirect_demand
        return [state for state in mps_view_states if state['id'] in self.ids]

    def get_impacted_mps_ids(self, domain=[]):
        supplying_domain = expression.AND([domain, [('warehouse_id', 'in', self.warehouse_id.ids), ('product_id', 'in', self.product_id._used_in_bom().ids)]])
        supplying_mps = self.env['mrp.production.schedule'].search(supplying_domain)

        supplied_domain = expression.AND([domain, [('warehouse_id', 'in', self.warehouse_id.ids), ('product_id', 'in', self.product_id._use_boms().ids)]])
        supplied_mps = self.env['mrp.production.schedule'].search(supplied_domain)

        return (supplying_mps | supplied_mps).ids

    def remove_replenish_qty(self, date_index):
        self.ensure_one()
        date_start, date_stop = self.company_id._get_mps_date_range()[date_index]
        forecasts = self.mrp_product_forecast_ids.filtered(
            lambda f: date_start <= f.date <= date_stop
        )
        if forecasts:
            forecasts.write({
                'replenish_qty': 0.0,
                'replenish_qty_updated': False,
            })
        return True

    def update_forecast_qty(self, date_index, quantity):
        self.ensure_one()
        date_start, date_stop = self.company_id._get_mps_date_range()[date_index]
        forecasts = self.mrp_product_forecast_ids.filtered(
            lambda f: date_start <= f.date <= date_stop
        )
        quantity = float_round(float(quantity), precision_rounding=self.product_uom_id.rounding)
        quantity_to_add = quantity - sum(forecasts.mapped('forecast_qty'))
        if forecasts:
            new_qty = float_round(forecasts[0].forecast_qty + quantity_to_add, precision_rounding=self.product_uom_id.rounding)
            forecasts[0].write({
                'forecast_qty': new_qty
            })
        else:
            forecast_vals = self._prepare_product_forecast_vals(date_stop, quantity, 0)
            forecasts.create(forecast_vals)
        return True

    def update_replenish_qty(self, date_index, quantity):
        self.ensure_one()
        date_start, date_stop = self.company_id._get_mps_date_range()[date_index]
        forecasts = self.mrp_product_forecast_ids.filtered(
            lambda f: date_start <= f.date <= date_stop
        )
        quantity = float_round(float(quantity), precision_rounding=self.product_uom_id.rounding)
        quantity_to_add = quantity - sum(forecasts.mapped('replenish_qty'))
        if forecasts:
            new_qty = float_round(forecasts[0].replenish_qty + quantity_to_add, precision_rounding=self.product_uom_id.rounding)
            forecasts[0].write({
                'replenish_qty': new_qty,
                'replenish_qty_updated': True
            })
        else:
            forecast_vals = self._prepare_product_forecast_vals(date_stop, 0, quantity)
            forecast_vals.update({'replenish_qty_updated': True})
            forecasts.create(forecast_vals)
        return True

    def _date_range_to_str(self, date_range):
        company = self.env.company
        date_range_str = []
        for start, stop in date_range:
            if company.manufacturing_period == 'month':
                date_range_str.append(format_date(self.env, start, date_format='MMM YYYY'))
            elif company.manufacturing_period == 'week':
                date_range_str.append(_('Week %s') % format_date(self.env, start, date_format='w'))
            else:
                date_range_str.append(format_date(self.env, start, date_format='MMM d'))
        return date_range_str

    def _prepare_product_forecast_vals(self, date, forecast_qty=0, replenish_qty=0, procurement_launched=False):
        self.ensure_one()
        return {
            'date': date,
            'forecast_qty': forecast_qty,
            'replenish_qty': replenish_qty,
            'procurement_launched': procurement_launched,
            'production_schedule_id': self.id,
        }

    def _get_move_qty_data(self, date_range, type):
        qty_data = defaultdict(float)
        qty_done_data = defaultdict(float)
        after_date = date_range[0][0]
        before_date = date_range[-1][1]
        domain_moves_confirmed, domain_moves_done = self._get_stock_move_domain(after_date, before_date, type)

        if type == 'incoming':  # If type is incoming, we need to take demand quantity from RFQs too
            rfq_domain = self._get_rfq_domain(after_date, before_date)
            rfq_lines = self.env['purchase.order.line'].search(rfq_domain, order='date_planned')
            i = 0
            for line in rfq_lines:
                while not (date_range[i][0] <= line.date_planned.date() <= date_range[i][1]):
                    i += 1
                quantity = line.product_uom._compute_quantity(line.product_qty, line.product_id.uom_id)
                key = (date_range[i], line.product_id, line.order_id.picking_type_id.warehouse_id)
                qty_data[key] += quantity
            loc_field = 'location_dest_id'

        else:
            additional_domain = [('raw_material_production_id', '=', False)]
            domain_moves_confirmed = expression.AND([domain_moves_confirmed, additional_domain])
            domain_moves_done = expression.AND([domain_moves_done, additional_domain])
            loc_field = 'location_id'

        stock_moves_confirmed = self.env['stock.move'].search(domain_moves_confirmed, order='date_expected')
        stock_moves_done = self.env['stock.move'].search(domain_moves_done, order='date')

        i = 0
        for move in stock_moves_confirmed:
            while not (date_range[i][0] <= move.date_expected.date() <= date_range[i][1]):
                i += 1
            location = getattr(move, loc_field)
            key = (date_range[i], move.product_id, location.get_warehouse())
            qty_data[key] += move.product_qty

        i = 0
        for move in stock_moves_done:
            while not (date_range[i][0] <= move.date.date() <= date_range[i][1]):
                i += 1
            location = getattr(move, loc_field)
            key = (date_range[i], move.product_id, location.get_warehouse())
            qty_done_data[key] += move.product_qty

        return qty_data, qty_done_data

    def _get_stock_move_domain(self, date_start, date_stop, type):
        if type == 'incoming':
            loc_field = 'location_dest_id'
            loc_dest_field = 'location_id'
        else:
            loc_field = 'location_id'
            loc_dest_field = 'location_dest_id'

        domain = [
            ('product_id', 'in', self.product_id.ids),
            ('inventory_id', '=', False),
            (loc_field, 'child_of', self.warehouse_id.view_location_id.ids),
            (loc_field + '.usage', '!=', 'inventory'),
            '|',
                (loc_dest_field + '.usage', 'not in', ('internal', 'inventory')),
                '&',
                    (loc_dest_field + '.usage', '=', 'internal'),
                    '!', (loc_dest_field, 'child_of', self.warehouse_id.view_location_id.ids),
        ]
        domain_confirmed = domain + [
            ('date_expected', '>=', date_start),
            ('date_expected', '<=', date_stop),
            ('state', 'not in', ['done', 'cancel', 'draft']),
        ]
        domain_done = domain + [
            ('date', '>=', date_start),
            ('date', '<=', date_stop),
            ('state', '=', 'done'),
        ]
        return domain_confirmed, domain_done

    def _get_rfq_domain(self, date_start, date_stop):
        return [
            ('product_id', 'in', self.product_id.ids),
            ('order_id.picking_type_id.default_location_dest_id', 'child_of', self.warehouse_id.view_location_id.ids),
            ('date_planned', '>=', date_start),
            ('date_planned', '<=', date_stop),
            ('state', 'in', ('draft', 'sent', 'to approve')),
        ]

    def _get_base_mps_view_states(self):
        fields_to_read = [
            'forecast_target_qty',
            'min_to_replenish_qty',
            'max_to_replenish_qty',
            'product_id',
        ]
        if self.env.user.has_group('stock.group_stock_multi_warehouses'):
            fields_to_read.append('warehouse_id')
        if self.env.user.has_group('uom.group_uom'):
            fields_to_read.append('product_uom_id')
        return self.read(fields_to_read)

    def _get_forecasts_state(self, mps_states, date_range, procurement_date):
        forecasts_state = defaultdict(list)
        for mps in self:
            forecast_vals = mps_states[mps.id]['mrp_product_forecast_ids']
            forced_replenish = True
            for index, (date_start, date_stop) in enumerate(date_range):
                forecast_state = {}
                forecast_val = forecast_vals[index]
                existing_forecasts = mps.mrp_product_forecast_ids.filtered(
                    lambda p: date_start <= p.date <= date_stop
                )
                procurement_launched = any(f.procurement_launched for f in existing_forecasts)

                # Compute correct state
                replenish_qty = forecast_val['replenish_qty']
                incoming_qty = forecast_val['incoming_qty']
                if incoming_qty == replenish_qty and (date_start <= procurement_date or procurement_launched):
                    forecast_state['state'] = 'launched'
                elif incoming_qty < replenish_qty and procurement_launched:
                    forecast_state['state'] = 'to_relaunch'
                elif incoming_qty > replenish_qty:
                    forecast_state['state'] = 'to_correct'
                else:
                    forecast_state['state'] = 'to_launch'

                forecast_state['forced_replenish'] = False
                forecast_state['to_replenish'] = False
                procurement_qty = replenish_qty - incoming_qty
                if forecast_state['state'] not in ('launched', 'to_correct') and procurement_qty > 0:
                    if date_start <= procurement_date:
                        forecast_state['to_replenish'] = True
                    if forced_replenish:
                        forecast_state['forced_replenish'] = True
                        forced_replenish = False

                forecasts_state[mps.id].append(forecast_state)
        return forecasts_state

    def _get_lead_times(self):
        product = self.product_id
        location = self.warehouse_id.lot_stock_id
        ProcurementGroup = self.env['procurement.group']
        rule = ProcurementGroup._get_rule(product, location, {})
        lead_time = 0

        while rule:
            lead_time += rule.delay
            if rule.action == 'manufacture':
                lead_time += product.produce_delay
            elif rule.action == 'buy':
                po_lead_time = self.env.company.po_lead
                supplier_lead_time = product.seller_ids[:1].delay
                lead_time += (po_lead_time + supplier_lead_time)
            if rule.procure_method == 'make_to_stock':
                break
            location = rule.location_src_id
            rule = ProcurementGroup._get_rule(product, location, {})

        return lead_time

    def _get_replenish_qty(self, after_forecast_qty):
        diff_qty = self.forecast_target_qty - after_forecast_qty
        if diff_qty > self.max_to_replenish_qty:
            replenish_qty = self.max_to_replenish_qty
        elif diff_qty < self.min_to_replenish_qty:
            replenish_qty = self.min_to_replenish_qty
        else:
            replenish_qty = diff_qty
        return replenish_qty

    def _get_indirect_demand_ordered(self, indirect_demand_trees):
        """ Order records in self so each MPS would be computed the state only once """

        def get_products_order(node):
            order_list = []
            if node.product in self.mapped('product_id'):
                if node.product not in products_ordered_temp:
                    order_list += node.product
            for child in node.children:
                order_list += get_products_order(child)
            return order_list

        products_ordered_temp = []
        for node in indirect_demand_trees:
            products_ordered_temp += get_products_order(node)

        mps_ordered = self.browse()
        for product in products_ordered_temp:
            mps_ordered |= self.filtered(lambda mps: mps.product_id == product)
        return mps_ordered

    def _get_indirect_demand_ratio(self, indirect_demand_trees, other_mps):
        """ Get the impact products ratio between a schedule and all of its related """
        self.ensure_one()
        other_mps = other_mps.filtered(lambda s: s.warehouse_id == self.warehouse_id)
        mps_ratio = []

        def first_match_mps(node, ratio, mps_ratio):
            if node.product == self.product_id:
                ratio = 1.0
            elif ratio and node.product in other_mps.mapped('product_id'):
                mps_ratio.append((other_mps.filtered(lambda s: s.product_id == node.product), ratio))
                return mps_ratio
            for child in node.children:
                mps_ratio = first_match_mps(child, ratio * child.ratio, mps_ratio)
                if not ratio and mps_ratio:
                    return mps_ratio
            return mps_ratio

        for tree in indirect_demand_trees:
            mps_ratio = first_match_mps(tree, False, [])
            if mps_ratio:
                break
        return mps_ratio

    def _get_bom_domain(self):
        return [
            '|',
                ('product_id', 'in', self.product_id.ids),
                '&',
                    ('product_id', '=', False),
                    ('product_tmpl_id', 'in', self.product_id.product_tmpl_id.ids)
        ]

    def _get_indirect_demand_tree(self):
        """ Reorder schedules in self and return a list of namedtuple:
            - On top: schedules without indirect demand
            - On lower: schedules which are more influenced by the others.
        """
        bom_domain = self._get_bom_domain()
        boms = self.env['mrp.bom'].search(bom_domain)

        Node = namedtuple('Node', ['product', 'ratio', 'children'])
        indirect_demand_tree = {}
        products_processed = {}

        def get_tree(product, ratio, products_processed):
            # if this tree is already processed, we dont need to recompute again
            product_tree = products_processed.get(product)
            if product_tree:
                return Node(product_tree.product, ratio, product_tree.children)

            product_tree = Node(product, ratio, [])
            product_boms = boms.filtered(
                lambda b: b.product_id == product or
                          not b.product_id and b.product_tmpl_id == product.product_tmpl_id
            )
            for line in product_boms.mapped('bom_line_ids'):
                line_qty = line.product_uom_id._compute_quantity(line.product_qty, line.product_id.uom_id)
                bom_qty = line.bom_id.product_uom_id._compute_quantity(line.bom_id.product_qty, line.bom_id.product_tmpl_id.uom_id)
                ratio = line_qty / bom_qty
                product_tree.children.append(get_tree(line.product_id, ratio, products_processed))
                if line.product_id in indirect_demand_tree:
                    indirect_demand_tree.pop(line.product_id)
            products_processed[product] = product_tree
            return product_tree

        for product in self.mapped('product_id'):
            if product in products_processed:
                continue
            indirect_demand_tree[product] = get_tree(product, 1.0, products_processed)

        return list(indirect_demand_tree.values())
