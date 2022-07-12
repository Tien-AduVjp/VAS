from psycopg2.extensions import AsIs

from odoo import models, api, _


##################################################
# Sổ chi tiết Vật liệu, Dụng cụ // Mẫu S10-DN TT200
##################################################
class Report_C200_S10dn(models.AbstractModel):
    _name = 'report.to_l10n_vn_stock_reports.report_c200_s10dn'
    _inherit = 'report.l10n_vn_stock.common'
    _description = 'Vietnam C200 S10-DN Report'

    def _prepare_opening_balance_line(self, product_id, company_id, date_from, location_ids, currency_id, dp, decimal_places):
        opening_balance = self.get_balance_at_date(product_id, company_id, date_from, location_ids)
        return {
            'ref': '',
            'date': '',
            'description': _('Opening Balance'),
            'unit_price': '',
            'in_qty': '',
            'in_total': '',
            'out_qty': '',
            'out_total': '',
            'inv_qty': opening_balance['qty'],
            'inv_total': opening_balance['value'],
            'notes': '',
            'currency': currency_id,
            'dp': dp,
            'decimal_places': decimal_places,
            'is_last_line': False
        }

    def _prepare_normal_line(self, item, currency_id, dp, decimal_places):
        StockLocation = self.env['stock.location'].with_context(active_test=False)
        PickingType = self.env['stock.picking.type'].with_context(active_test=False)
        StockPicking = self.env['stock.picking']
        if item['operation_type'] == 'in':
            src_loc_name = StockLocation.browse(item['counter_location_id']).display_name
            dest_loc_name = StockLocation.browse(item['location_id']).display_name
        else:
            src_loc_name = StockLocation.browse(item['location_id']).display_name
            dest_loc_name = StockLocation.browse(item['counter_location_id']).display_name
        picking_type_id = PickingType.browse(item['picking_type_id'])
        item['description'] = _("Moved from '%s' to '%s'") % (src_loc_name, dest_loc_name)
        if picking_type_id:
            item['description'] = "%s, %s" % (picking_type_id.name, item['description'])
        stock_picking = StockPicking.browse(item['picking_id'])
        if stock_picking and stock_picking.name:
            ref = stock_picking.name
        elif item['origin']:
            ref = item['origin']
        elif item['description']:
            ref = item['description']
        item['note'] = ''
        if stock_picking and stock_picking.note:
            item['note'] += stock_picking.note
        return {
            'ref': ref,
            'date': self._formart_datetime_to_date(item['date']),
            'description': item['description'],
            'unit_price': item['price_unit'],
            'in_qty': item['in_qty'],
            'in_total': item['in_total'],
            'out_qty': item['out_qty'],
            'out_total': item['out_total'],
            'inv_qty': item['inv_qty'],
            'inv_total': item['inv_total'],
            'notes': item['note'] or item['move_note'],
            'currency': currency_id,
            'dp': dp,
            'decimal_places': decimal_places,
            'is_last_line': False
        }

    def _prepare_sum_line(self, currency_id, dp, decimal_places, sum_line=None, item=None, last_line=False):
        sum_line = sum_line or {
            'in_qty': 0.0,
            'in_total': 0.0,
            'out_qty': 0.0,
            'out_total': 0.0,
            'inv_qty': 0.0,
            'inv_total': 0.0,
            'currency': currency_id,
            'dp': dp,
            'decimal_places': decimal_places,
            'is_last_line': True,
            }
        if item:
            if last_line:
                sum_line['inv_qty'] += item['inv_qty']
                sum_line['inv_total'] += item['inv_total']
            else:
                sum_line['in_qty'] += item['in_qty']
                sum_line['in_total'] += item['in_total']
                sum_line['out_qty'] += item['out_qty']
                sum_line['out_total'] += item['out_total']
        return sum_line

    def _prefetching(self, res_lines):
        StockLocation = self.env['stock.location'].with_context(active_test=False)
        PickingType = self.env['stock.picking.type'].with_context(active_test=False)
        StockPicking = self.env['stock.picking']
        picking_type_ids = []
        picking_ids = []
        location_ids = []
        for item in res_lines:
            location_ids += [item['location_id'], item['counter_location_id']]
            if item['picking_type_id']:
                picking_type_ids.append(item['picking_type_id'])
            if item['picking_id']:
                picking_ids.append(item['picking_id'])

        # prefetching for better performance
        location_ids = StockLocation.browse(location_ids)
        location_ids.read(['display_name'])
        picking_type_ids = PickingType.browse(picking_type_ids)
        picking_type_ids.read(['name'])
        picking_ids = StockPicking.browse(picking_ids)
        picking_ids.read(['name'])

    @api.model
    def _get_lines(self, data):
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        product_id = data['form']['product_id'][0]
        company_id = data['form']['company_id'][0]
        location_ids = tuple(self.get_locations_for_query(data).ids)

        dp = 'Product Unit of Measure'
        currency_id = self.env['res.company'].browse(data['form']['company_id'][0]).currency_id
        decimal_places = currency_id.decimal_places
        res = []
        res.append(self._prepare_opening_balance_line(product_id, company_id, date_from, location_ids, currency_id, dp, decimal_places))
        stock_history = self.get_stock_history_query(company_id, location_ids, date_to=date_to, product_id=product_id)
        sql = """
        WITH stock_history AS (%s)
        SELECT sh.*,
            CASE WHEN operation_type = 'in'
                THEN sh.quantity
                ELSE 0.0
                END AS in_qty,
            CASE WHEN operation_type = 'in'
                THEN sh.quantity * sh.price_unit
                ELSE 0.0
                END AS in_total,
            CASE WHEN operation_type = 'out'
                THEN -1 * sh.quantity
                ELSE 0.0
                END AS out_qty,
            CASE WHEN operation_type = 'out'
                THEN -1 * sh.quantity * sh.price_unit
                ELSE 0.0
                END AS out_total,
            sh.commulative_qty AS inv_qty,
            sh.commulative_value AS inv_total
        FROM stock_history AS sh
        WHERE sh.date >= %s AND sh.date < %s
            AND sh.product_id = %s
            AND sh.counter_location_id not in %s
        ORDER BY sh.date ASC
        """
        self.env.cr.execute(sql, (AsIs(stock_history), date_from, date_to, product_id, location_ids))
        res_lines = self.env.cr.dictfetchall()
        self._prefetching(res_lines)

        # initiate the last/summary line data
        sum_line = self._prepare_sum_line(currency_id, dp, decimal_places)
        lines_count = len(res_lines)
        i = 0
        for item in res_lines:
            i += 1
            item = self._prepare_normal_line(item, currency_id, dp, decimal_places)
            res.append(item)
            sum_line = self._prepare_sum_line(currency_id, dp, decimal_places, sum_line, item)
            if i == lines_count:  # the last line
                sum_line = self._prepare_sum_line(currency_id, dp, decimal_places, sum_line, item, last_line=lines_count)
                res.append(sum_line)
        return res
