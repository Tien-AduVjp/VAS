from psycopg2.extensions import AsIs

from odoo import models, api
from odoo.tools.misc import formatLang


###############################################
# Bảng kê Xuất - Nhập - Tồn // Mẫu S11-DN TT200
###############################################
class Report_C200_S11dn(models.AbstractModel):
    _name = 'report.to_l10n_vn_stock_reports.report_c200_s11dn'
    _inherit = 'report.l10n_vn_stock.common'
    _description = 'Vietnam C200 S11-DN Report'

    def _get_prefetching_fields(self):
        return ['display_name', 'uom_id']

    def _prefetching(self, res_lines):
        ProductProduct = self.env['product.product'].with_context(active_test=False)
        ids = []
        company_ids = []
        for item in res_lines:
            ids.append(item['product_id'])
            company_ids.append(item['company_id'])
        all_product_ids = ProductProduct.browse(ids)
        all_product_ids.read(self._get_prefetching_fields())

    @api.model
    def _get_lines(self, data):
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        company_id = data['form']['company_id'][0]
        product_categ_id = data['form']['product_categ_id'] and data['form']['product_categ_id'][0] or None

        # for formating support
        dp = 'Product Unit of Measure'
        currency_id = self.env['res.company'].browse(data['form']['company_id'][0]).currency_id
        decimal_places = currency_id.decimal_places

        res = []
        location_ids = tuple(self.get_locations_for_query(data).ids)  # this also includes the given locations
        stock_history = self.get_stock_history_query(company_id, location_ids, product_categ_id=product_categ_id)
        res_lines = self._res_lines(stock_history, date_from, location_ids, date_to)
        self._prefetching(res_lines)
        sum_line = self._prepare_sum_line()
        lines_count = len(res_lines)
        i = 0
        for item in res_lines:
            i += 1
            sum_line = self._prepare_sum_line(decimal_places, sum_line, item)
            normal_line_item = self._prepare_normal_line(item, decimal_places, dp)
            res.append(normal_line_item)
            if i == lines_count:  # the last line
                sum_line = self._prepare_sum_line(decimal_places, sum_line, item, lines_count)
                res.append(sum_line)
        return res

    def _prepare_normal_line(self, item, decimal_places, dp):
        ProductProduct = self.env['product.product'].with_context(active_test=False)
        product = ProductProduct.browse(item['product_id'])
        res = item.copy()  # we don't want to modify the item
        res['product_name'] = product.display_name
        res['product_uom'] = product.uom_id.name
        res['last_invt_qty'] = formatLang(self.env, item['last_invt_qty'], dp=dp)
        res['stock_in_val'] = formatLang(self.env, item['stock_in_val'], digits=decimal_places)
        res['cur_invt_qty'] = formatLang(self.env, item['cur_invt_qty'], dp=dp)
        res['stock_in_qty'] = formatLang(self.env, item['stock_in_qty'], dp=dp)
        res['cur_invt_val'] = formatLang(self.env, item['cur_invt_val'], digits=decimal_places)
        res['stock_out_qty'] = formatLang(self.env, item['stock_out_qty'], dp=dp)
        res['last_invt_val'] = formatLang(self.env, item['last_invt_val'], digits=decimal_places)
        res['stock_out_val'] = formatLang(self.env, item['stock_out_val'], digits=decimal_places)
        res['is_last_line'] = False
        return res

    def _prepare_sum_line(self, decimal_places=None, sum_line=None, item=None, last_line=False):
        sum_line = sum_line or {
            'last_invt_val': 0.0,
            'stock_in_val': 0.0,
            'stock_out_val': 0.0,
            'cur_invt_val': 0.0,
            'is_last_line': True
            }
        if item:
            if last_line:
                sum_line['last_invt_val'] = formatLang(self.env, sum_line['last_invt_val'], digits=decimal_places)
                sum_line['stock_in_val'] = formatLang(self.env, sum_line['stock_in_val'], digits=decimal_places)
                sum_line['stock_out_val'] = formatLang(self.env, sum_line['stock_out_val'], digits=decimal_places)
                sum_line['cur_invt_val'] = formatLang(self.env, sum_line['cur_invt_val'], digits=decimal_places)
            else:
                sum_line['last_invt_val'] += item['last_invt_val']
                sum_line['stock_in_val'] += item['stock_in_val']
                sum_line['stock_out_val'] += item['stock_out_val']
                sum_line['cur_invt_val'] += item['cur_invt_val']
        return sum_line

    def _res_lines(self, stock_history, date_from, location_ids, date_to):
        sql = """
        WITH tmp_tbl_sh AS(
            WITH stock_history AS(
                %s
            )
            SELECT m.product_id, m.company_id, SUM(m.quantity) AS total_quantity, SUM (m.price_unit * m.quantity) AS inventory_value, 'last_inventory' AS inventory_type
                FROM stock_history AS m
                WHERE m.date < %s
                GROUP BY m.product_id, m.company_id
            UNION ALL(
            SELECT m.product_id, m.company_id, SUM(m.quantity) AS total_quantity, SUM (m.price_unit * m.quantity) AS inventory_value, 'stock_in' AS inventory_type
                FROM stock_history AS m
                WHERE m.date >= %s AND m.date < %s AND m.operation_type = 'in' AND m.counter_location_id NOT IN %s
                GROUP BY m.product_id, m.company_id
            )
            UNION ALL(
            SELECT m.product_id, m.company_id, SUM(m.quantity) AS total_quantity, SUM (m.price_unit * m.quantity) AS inventory_value, 'stock_out' AS inventory_type
                FROM stock_history AS m
                WHERE m.date >= %s AND m.date < %s AND m.operation_type = 'out' AND m.counter_location_id NOT IN %s
                GROUP BY m.product_id, m.company_id
            )
            UNION ALL (
            SELECT m.product_id, m.company_id, SUM(m.quantity) AS total_quantity, SUM (m.price_unit * m.quantity) AS inventory_value, 'current_inventory' AS inventory_type
                FROM stock_history AS m
                WHERE m.date < %s
                GROUP BY m.product_id, m.company_id
            )
        )
        SELECT sh.product_id, sh.company_id,
        p.default_code AS product_code,
        MAX(CASE WHEN sh.inventory_type = 'last_inventory' THEN sh.total_quantity ELSE 0.0 END) AS last_invt_qty,
        MAX(CASE WHEN sh.inventory_type = 'last_inventory' THEN sh.inventory_value ELSE 0.0 END) AS last_invt_val,
        MAX(CASE WHEN sh.inventory_type = 'stock_in' THEN sh.total_quantity ELSE 0.0 END) AS stock_in_qty,
        MAX(CASE WHEN sh.inventory_type = 'stock_in' THEN sh.inventory_value ELSE 0.0 END) AS stock_in_val,
        MAX(CASE WHEN sh.inventory_type = 'stock_out' THEN ABS(sh.total_quantity) ELSE 0.0 END) AS stock_out_qty,
        MAX(CASE WHEN sh.inventory_type = 'stock_out' THEN ABS(sh.inventory_value) ELSE 0.0 END) AS stock_out_val,
        MAX(CASE WHEN sh.inventory_type = 'current_inventory' THEN sh.total_quantity ELSE 0.0 END) AS cur_invt_qty,
        MAX(CASE WHEN sh.inventory_type = 'current_inventory' THEN sh.inventory_value ELSE 0.0 END) AS cur_invt_val

        FROM tmp_tbl_sh AS sh
        LEFT JOIN product_product AS p ON p.id =  sh.product_id

        GROUP BY sh.product_id, sh.company_id, p.default_code
        ORDER BY sh.product_id
        """
        self.env.cr.execute(sql, (AsIs(stock_history), date_from, date_from, date_to, location_ids, date_from, date_to, location_ids, date_to))
        return self.env.cr.dictfetchall()
