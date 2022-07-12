import logging

from datetime import timedelta, datetime

from odoo import models, api, _, fields

_logger = logging.getLogger(__name__)


class StockAgeReport(models.AbstractModel):
    _name = "stock.age.report"
    _description = "Stock Age Report"
    _inherit = 'stock.report.abstract'

    filter_periods = {'date': '', 'filter': 'default', 'period_length':'30', 'number_of_period':'5'}
    filter_current_product = {'product_category_id': 1, 'product_id': 'all'}
    filter_current_warehouse_location = {'warehouse_id': '', 'location_id': ''}
    filter_unfold_all = False
    
    def get_columns_name(self, options):
        columns = [{}]
        number_of_period = int(options['periods']['number_of_period'])
        period_length = int(options['periods']['period_length'])
        columns_name = []
        i = 0
        for val in range(number_of_period):
            col_name = ""
            if i == number_of_period - 1:
                col_name = "%s+" % (period_length * val)
            else:
                col_name = "%s - %s" % (period_length * val, period_length * (val + 1))
            columns_name.append(col_name)
            i += 1
        columns += [{'name': v, 'class': 'number', 'style': 'white-space:nowrap;', 'colspan': 2} for v in columns_name]
        return columns

    @api.model
    def get_lines(self, options):
        query = self._prepare_sql(options)
        self.env.cr.execute(query)
        rows = self.env.cr.fetchall()
        if not rows:
            return
        
        # prefetching for better perfomance later
        product_ids = list(map(lambda row: row[0], rows))
        ProductProduct = self.env['product.product']
        product_ids = ProductProduct.browse(product_ids)
        product_ids.read(['default_code', 'name', 'categ_id'])

        final_rows = []
        sum_row = []
        
        def add(a, b):
            if a and b:
                return a + b
            elif a:
                return a
            elif b:
                return b
            else:
                return 0
        
        for row in map(list, rows):
            if not sum_row:
                sum_row = row.copy()
            else:
                sum_row = list(map(add, sum_row, row))
            
            product = ProductProduct.browse(row[0])
            row.insert(1, product.default_code)
            row.insert(2, product.display_name)
            row.insert(3, product.categ_id.name)
            final_rows.append(row)
        
        # convert zero to None to avoid display zero on excel cells on the sum line
        sum_row = list(map(lambda row: row if row else None, sum_row))
        
        final_rows.append(sum_row)
        return final_rows

    def get_report_name(self):
        return _("Stock Age Report")

    def get_parent_name(self, category):
        name = category.name
        if category.parent_id:
            name = self.get_parent_name(category.parent_id) + ' / ' + name
        return name
    
    def get_parent_location_name(self, location):
        name = location.name
        if location.location_id.location_id:
            name = self.get_parent_location_name(location.location_id) + ' / ' + name
        return name
    
    def _select(self, stock_age_query, intervals):
        sub = ""
        for interval in intervals:
            sub += """,
            CASE WHEN s.interval = '%s'
                THEN SUM(s.qty)
                END AS %s,
            CASE WHEN s.interval = '%s'
                THEN SUM(s.valuation)
                END AS %s
            """ % (interval,
                   'qty_' + interval.replace(' - ', '_to_').replace(' + ', '_or_more'),
                   interval,
                   'valuation_' + interval.replace(' - ', '_to_').replace(' + ', '_or_more'))

        return """
        WITH stock_age AS (%s)
        SELECT
            s.product_id
            %s
        """ % (stock_age_query, sub)

    def _from(self):
        return """
        FROM stock_age AS s
        JOIN product_product AS p ON p.id =  s.product_id
        """

    def _group_by(self):
        return """
        GROUP BY s.product_id, s.interval
        """

    def get_child_locations(self, locations):
        """
        #TODO: remove me in master
        Method to find all recursive child locations of the input location
        then return them all (include the input location) in a stock.location record set

        @param location_id: the parent location
        @return: recordset of the location and its recursive child
        """
        _logger.warning("The method `get_child_locations()` is deprecated. Please use `locations._get_recursive_children()` instead.")
        return locations._get_recursive_children()

    def _sub_select(self, interval):
        return """
            SELECT
                svl.product_id,
                svl.remaining_qty AS qty,
                svl.remaining_value AS valuation,
                '%s' AS interval
        """ % (interval,)

    def _sub_from(self):
        return """
            FROM stock_valuation_layer AS svl
                JOIN product_product AS p ON p.id = svl.product_id
                JOIN product_template AS tmpl ON tmpl.id = p.product_tmpl_id
                JOIN stock_move AS sm ON sm.id = svl.stock_move_id
                JOIN stock_location AS loc ON loc.id = sm.location_dest_id
        """

    def _sub_where(self, from_date, to_date, options):
        sql = """
        WHERE
        """
        if from_date:
            sql += """
                svl.create_date > '%s'
            AND
            """%(from_date)
        sql += """
        svl.create_date <= '%s'
        """ % (to_date)
        
        location_id = options['current_warehouse_location'].get('location_id', False)
        if location_id and location_id != 'all':
            locations = self.env['stock.location'].browse(int(location_id))
        else:
            warehouse_id = options['current_warehouse_location'].get('warehouse_id', False)
            if warehouse_id and warehouse_id != 'all':
                locations = self.env['stock.location'].search([
                    ('usage', 'in', ('internal', 'transit')),
                    ('warehouse_id', '=', warehouse_id)
                    ])
            else:
                locations = self.env['stock.location']
        
        if locations:
            locations = locations._get_recursive_children()
            sql += """
                AND loc.id IN (%s)
            """ % (",".join([str(item) for item in locations.ids]),)
        
        if options.get('multi_company'):
            company_id = False
            for company_id in options['multi_company']:
                if company_id['selected']:
                    company_id = company_id['id']
                    break
            if company_id:
                sql += """
                    AND svl.company_id = %s
                """ % (company_id,)
        
        product_category_id = options['current_product']['product_category_id']
        if product_category_id and product_category_id != 1:
            sql += """
                AND tmpl.categ_id = %s
            """ % (product_category_id,)
        
        product_id = options['current_product']['product_id']
        if product_id and product_id != 'all':
            sql += """
                AND svl.product_id = %s
            """ % (product_id,)
        return sql

    def _sub_group_by(self):
        return """
            GROUP BY
                svl.id
        """

    def _prepare_sql(self, options):
        to_date = fields.Date.to_date(options['periods']['date']) or fields.Date.context_today(self)
        no_of_ped = int(options['periods']['number_of_period'])
        period_length = int(options['periods']['period_length'])
        
        to_date = datetime.combine(to_date, datetime.max.time())
        
        sql1 = ""
        intervals = []
        for i in range(no_of_ped):
            new_date = to_date - timedelta(days=period_length)
            if i == no_of_ped - 1:
                interval = '{} + '.format(period_length * i)
                union = ""
                new_date = False
            else:
                interval = '{} - {}'.format(i * period_length, (i + 1) * period_length)
                union = "UNION ALL"
            intervals.append(interval)

            sql1 += """
            %s
            %s
            %s
            %s
            %s
            """ % (self._sub_select(interval),
                   self._sub_from(),
                   self._sub_where(new_date, to_date, options),
                   self._sub_group_by(),
                   union
                   )
            to_date = new_date

        sql = """
        %s
        %s
        %s
        """ % (self._select(sql1, intervals), self._from(), self._group_by())

        final_sql = """
        %s
        %s
        %s
        """ % (self._final_select(sql, intervals), self._final_from(), self._final_group_by())

        return final_sql

    def _final_select(self, sql, intervals):
        final = ""
        for interval in intervals:
            final += """,
            SUM(%s) AS qty,
            SUM(%s) AS valuation
             """ % ('qty_' + interval.replace(' - ', '_to_').replace(' + ', '_or_more'),
                   'valuation_' + interval.replace(' - ', '_to_').replace(' + ', '_or_more'))

        return"""
        WITH tempo_table AS (%s)
        SELECT
            t.product_id
            %s
        """ % (sql, final)

    def _final_from(self):
        return"""
        FROM tempo_table AS t
        """

    def _final_group_by(self):
        return"""
        GROUP BY t.product_id
        """
