from psycopg2.extensions import AsIs

from odoo import models, api


class ReportStockInOut(models.AbstractModel):
    _name = 'report.to_l10n_vn_stock_reports.report_stockinout'
    _inherit = 'report.l10n_vn_stock.common'
    _description = 'Vietnam C200 Stock In/Out Report'

    def _prefetching(self, res_lines):
        StockLocation = self.env['stock.location'].with_context(active_test=False)
        StockPicking = self.env['stock.picking']
        ProductProduct = self.env['product.product'].with_context(active_test=False)
        picking_ids = []
        location_ids = []
        product_ids = []
        for item in res_lines:
            product_ids.append(item['product_id'])
            location_ids += [item['location_id'], item['counter_location_id']]
            if item['picking_id']:
                picking_ids.append(item['picking_id'])

        # prefetching for better performance
        location_ids = StockLocation.browse(location_ids)
        location_ids.read(['display_name'])
        picking_ids = StockPicking.browse(picking_ids)
        picking_ids.read(['name'])
        product_ids = ProductProduct.browse(product_ids)
        product_ids.read(['uom_id', 'display_name'])

    @api.model
    def _get_lines(self, data):
        res = []
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        company_id = data['form']['company_id'][0]
        location_ids = tuple(self.get_locations_for_query(data).ids)
        operation_type = data['form']['type']
        dp = 'Product Unit of Measure'
        currency_id = self.env['res.company'].browse(company_id).currency_id
        decimal_places = currency_id.decimal_places
        stock_history = self.get_stock_history_query(company_id, location_ids, date_from=date_from, date_to=date_to, operation_type=operation_type)
        res_lines = self._res_lines(stock_history, date_from, date_to, location_ids)
        self._prefetching(res_lines)
        # initiate the last/summary line data
        sum_line = self._prepare_sum_line(dp, decimal_places)
        lines_count = len(res_lines)
        i = 0
        for item in res_lines:
            i += 1
            item = self._prepare_normal_line(item, dp, decimal_places, operation_type)
            res.append(item)
            sum_line = self._prepare_sum_line(dp, decimal_places, sum_line, item)
            if i == lines_count:  # the last line
                res.append(sum_line)
        return res

    def _prepare_normal_line(self, item, dp, decimal_places, operation_type):
        StockLocation = self.env['stock.location'].with_context(active_test=False)
        StockPicking = self.env['stock.picking']
        ProductProduct = self.env['product.product'].with_context(active_test=False)
        product = ProductProduct.browse(item['product_id'])
        item['product_code'] = product.default_code
        if operation_type == 'in':
            src_loc_name = StockLocation.browse(item['counter_location_id']).display_name
            dest_loc_name = StockLocation.browse(item['location_id']).display_name
        else:
            src_loc_name = StockLocation.browse(item['location_id']).display_name
            dest_loc_name = StockLocation.browse(item['counter_location_id']).display_name
        stock_picking = StockPicking.browse(item['picking_id'])
        item['reference'] = stock_picking.name if stock_picking else ''
        item['src_loc_name'] = src_loc_name
        item['dest_loc_name'] = dest_loc_name
        item['product_name'] = product.display_name
        item['product_uom'] = product.uom_id.name
        item['dp'] = dp
        item['decimal_places'] = decimal_places
        item['is_last_line'] = False
        item['date'] = self._formart_datetime_to_date(item['date'])
        return item

    def _prepare_sum_line(self, dp, decimal_places, sum_line=None, item=None):
        sum_line = sum_line or {
            'qty': 0.0,
            'total_price': 0.0,
            'dp': dp,
            'decimal_places': decimal_places,
            'is_last_line': True
            }
        if item:
            sum_line['qty'] += item['qty']
            sum_line['total_price'] += item['total_price']
        return sum_line

    def _res_lines(self, stock_history, date_from, date_to, location_ids):
        sql = """
        WITH stock_history AS (%s)
        SELECT
            sh.move_id,
            sh.quantity,
            sh.price_unit AS unit_price,
            sh.product_id,
            sh.date,
            sh.move_note AS note,
            sh.origin,
            sh.description,
            sh.location_id,
            sh.counter_location_id,
            sh.picking_id,
            CASE WHEN operation_type = 'out'
                THEN -1 * sh.quantity * sh.price_unit
                ELSE sh.quantity * sh.price_unit
                END AS total_price,
            CASE WHEN operation_type = 'out'
                THEN -1 * sh.quantity
                ELSE sh.quantity
                END AS qty
        FROM stock_history AS sh
        WHERE sh.date >= %s AND sh.date < %s
            AND sh.counter_location_id not in %s
        ORDER BY sh.date ASC
        """
        self.env.cr.execute(sql, (AsIs(stock_history), date_from, date_to, location_ids))
        return self.env.cr.dictfetchall()
