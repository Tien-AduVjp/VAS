from psycopg2.extensions import AsIs

from odoo import models, api, _


#############################
# Thẻ kho // Mẫu S12-DN TT200
#############################
class Report_C200_S12dn(models.AbstractModel):
    _name = 'report.to_l10n_vn_stock_reports.report_c200_s12dn'
    _inherit = 'report.l10n_vn_stock.common'
    _description = 'Vietnam C200 S12-DN Report'

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
        res = []
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        product_id = data['form']['product_id'][0]
        location_ids = tuple(self.get_locations_for_query(data).ids)
        company_id = data['form']['company_id'][0]
        stock_history = self.get_stock_history_query(company_id, location_ids, date_to=date_to, product_id=product_id)
        res_lines = self._res_lines(stock_history, date_from, date_to, product_id, location_ids)
        self._prefetching(res_lines)
        dp = 'Product Unit of Measure'
        sum_line = self._prepare_sum_line(dp)
        i = 0
        lines_count = len(res_lines)
        for item in res_lines:
            i += 1
            item = self._prepare_normal_line(item, dp)
            res.append(item)
            sum_line = self._prepare_sum_line(dp, sum_line, item)
            if i == lines_count:
                sum_line = self._prepare_sum_line(dp, sum_line, item, last_line=lines_count)
                res.append(sum_line)
        return res

    def _prepare_normal_line(self, item, dp):
        StockLocation = self.env['stock.location'].with_context(active_test=False)
        PickingType = self.env['stock.picking.type'].with_context(active_test=False)
        StockPicking = self.env['stock.picking']
        item['dp'] = dp
        if item['operation_type'] == 'in':
            src_loc_name = StockLocation.browse(item['counter_location_id']).display_name
            dest_loc_name = StockLocation.browse(item['location_id']).display_name
        else:
            src_loc_name = StockLocation.browse(item['location_id']).display_name
            dest_loc_name = StockLocation.browse(item['counter_location_id']).display_name
        item['src_loc_name'] = src_loc_name
        item['dest_loc_name'] = dest_loc_name
        stock_picking = StockPicking.browse(item['picking_id'])
        item['move_date'] = self._formart_datetime_to_date(item['move_date'])
        item['scheduled_date'] = self._formart_datetime_to_date(stock_picking.scheduled_date) if stock_picking else item['move_date']
        item['reference'] = stock_picking.name if stock_picking else item['source']
        picking_type_id = PickingType.browse(item['picking_type_id'])
        item['description'] = _("Moved from '%s' to '%s'") % (src_loc_name, dest_loc_name)
        if picking_type_id:
            item['description'] = "%s, %s" % (picking_type_id.name, item['description'])
        item['is_last_line'] = False
        return item

    def _prepare_sum_line(self, dp, sum_line=None, item=None, last_line=False):
        sum_line = sum_line or {
            'sum_in_qty': 0.0,
            'sum_out_qty': 0.0,
            'inv_qty': 0.0,
            'is_last_line': True,
            'dp': dp
            }
        if item:
            if last_line:
                sum_line['inv_qty'] += item['inv_qty']
            else:
                sum_line['sum_in_qty'] += item['in_qty']
                sum_line['sum_out_qty'] += item['out_qty']
        return sum_line

    def _res_lines(self, stock_history, date_from, date_to, product_id, location_ids):
        sql = """
        WITH stock_history AS (%s)
        SELECT
            sh.date AS move_date,
            sh.origin AS source,
            location_id,
            counter_location_id,
            picking_type_id,
            picking_id,
            operation_type,
            move_note AS note,
            CASE WHEN operation_type = 'in'
                THEN sh.quantity
                ELSE 0.0
                END AS in_qty,
            CASE WHEN operation_type = 'out'
                THEN -1 * sh.quantity
                ELSE 0.0
                END AS out_qty,
            sh.commulative_qty AS inv_qty
        FROM stock_history AS sh
        WHERE sh.date >= %s AND sh.date < %s
            AND sh.product_id = %s
            AND sh.counter_location_id not in %s
        ORDER BY sh.date ASC
        """
        self.env.cr.execute(sql , (AsIs(stock_history), date_from, date_to, product_id, location_ids,))
        return self.env.cr.dictfetchall()
