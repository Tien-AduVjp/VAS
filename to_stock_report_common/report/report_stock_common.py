from odoo import models, api
from psycopg2.extensions import AsIs


class ReportStockCommon(models.AbstractModel):
    _name = 'report.stock.common'
    _description = 'Report Stock Common'

    def get_locations_for_query(self, data):
        form_location_id = data['form']['location_id']
        StockLocation = self.env['stock.location'].with_context(active_test=False)
        if form_location_id:
            location_id = StockLocation.browse(form_location_id[0])
            location_ids = location_id.get_sublocations()  # This also includes the given parent location
        else:
            domain = [('usage', 'in', ('internal', 'transit'))]
            form_company_id = data['form']['company_id']
            if form_company_id:
                domain += [('company_id', '=', form_company_id[0])]

            location_ids = StockLocation.search(domain)

        return location_ids

    def _get_date_condition(self, date_from=None, date_to=None):
        date_query = ""
        if date_from:
            date_query += " AND m.date >= '%s'" % date_from
        if date_to:
            date_query += " AND m.date <= '%s'" % date_to
        return date_query

    def _get_product_category_condition(self, product_categ_id=None):
        product_categ_query = ""
        if product_categ_id:
            product_categ_query += " AND categ.id = %s" % product_categ_id
        return product_categ_query

    def _get_product_template_condition(self, product_tmpl_id=None):
        product_tmpl_query = ""
        if product_tmpl_id:
            product_tmpl_query += " AND product_template.id = %s" % product_tmpl_id
        return product_tmpl_query

    def _get_product_condition(self, product_id=None):
        product_query = ""
        if product_id:
            product_query += " AND product_product.id = %s" % product_id
        return product_query

    def _get_stock_move_svl_query(self):
        return """
        SELECT
            m.id AS id,
            m.product_id AS product_id,
            m.date AS date,
            m.note AS note,
            m.origin AS origin,
            m.name AS name,
            m.picking_id AS picking_id,
            m.picking_type_id AS picking_type_id,
            COALESCE(SUM(svl.value) / NULLIF(SUM(svl.quantity), 0), 0) AS price_unit
        FROM
            stock_move AS m
            LEFT JOIN stock_valuation_layer AS svl ON m.id = svl.stock_move_id
        GROUP BY
            m.id,
            m.product_id,
            m.date,
            m.note,
            m.origin,
            m.name,
            m.picking_id,
            m.picking_type_id
        """

    #---------------------------------
    # STOCK IN
    #---------------------------------
    def _select_stock_in(self):
        return """
        SELECT
            sml.id AS id,
            m.id AS move_id,
            sp.id AS picking_id,
            pkt.id AS picking_type_id,
            dest_location.id AS location_id,
            source_location.id AS counter_location_id,
            dest_location.company_id AS company_id,
            m.product_id AS product_id,
            product_template.id AS product_template_id,
            product_template.categ_id AS product_categ_id,
            sml.qty_done / sml_uom.factor * product_tmpl_uom.factor AS quantity,
            m.date AS date,
            m.note AS move_note,
            m.price_unit AS price_unit,
            m.origin,
            m.name AS description,
            stock_production_lot.name AS serial_number,
            'in'::text AS operation_type
        """

    def _from_stock_in(self):
        return """
        FROM
            stock_move_line as sml
        JOIN
            stock_move_svl AS m ON m.id = sml.move_id
        LEFT JOIN
            stock_production_lot ON stock_production_lot.id = sml.lot_id
        JOIN
            stock_location dest_location ON sml.location_dest_id = dest_location.id
        JOIN
            stock_location source_location ON sml.location_id = source_location.id
        JOIN
            product_product ON product_product.id = m.product_id
        JOIN
            product_template ON product_template.id = product_product.product_tmpl_id
        JOIN
            product_category AS categ ON categ.id = product_template.categ_id
        JOIN 
            uom_uom AS sml_uom ON sml_uom.id = sml.product_uom_id
        JOIN 
            uom_uom AS product_tmpl_uom ON product_tmpl_uom.id = product_template.uom_id
        LEFT JOIN
            stock_picking AS sp ON sp.id = m.picking_id
        LEFT JOIN
            stock_picking_type AS pkt ON pkt.id = m.picking_type_id
        """

    def _where_stock_in(self, company_id, stock_loc_condition, date_query, product_tmpl_query, product_query, product_categ_query):
        return """
        WHERE sml.state = 'done' AND dest_location.usage IN ('internal', 'transit') AND dest_location.company_id = {0}
            AND (
                NOT (source_location.company_id is null AND dest_location.company_id is null) OR
                source_location.company_id != dest_location.company_id OR
                source_location.usage NOT IN ('internal', 'transit'))
            {1}
            {2}
            {3}
            {4}
            {5}
            {6}
        """.format(company_id, stock_loc_condition, date_query, product_tmpl_query, product_query, product_categ_query, self._add_custom_filter_data())

    def _get_stock_in_query(self, company_id, location_ids=[], date_from=None, date_to=None, product_tmpl_id=None, product_id=None, product_categ_id=None):
        stock_loc_condition = ""
        if len(location_ids) > 1:
            stock_loc_condition = " AND dest_location.id IN {0}".format(location_ids)
        elif len(location_ids) == 1:
            stock_loc_condition = " AND dest_location.id = {0}".format(location_ids[0])

        date_query = self._get_date_condition(date_from=date_from, date_to=date_to)
        product_tmpl_query = self._get_product_template_condition(product_tmpl_id)
        product_query = self._get_product_condition(product_id)
        product_categ_query = self._get_product_category_condition(product_categ_id)
        sql = """
                {0}
                {1}
                {2}
        """.format(
            self._select_stock_in(),
            self._from_stock_in(),
            self._where_stock_in(company_id, stock_loc_condition, date_query, product_tmpl_query, product_query, product_categ_query)
            )
        return sql

    #---------------------------------
    # STOCK OUT
    #---------------------------------
    def _select_stock_out(self):
        return """
        SELECT
            (-1) * sml.id AS id,
            m.id AS move_id,
            sp.id AS picking_id,
            pkt.id AS picking_type_id,
            source_location.id AS location_id,
            dest_location.id AS counter_location_id,
            source_location.company_id AS company_id,
            m.product_id AS product_id,
            product_template.id AS product_template_id,
            product_template.categ_id AS product_categ_id,
            (-1) * sml.qty_done / sml_uom.factor * product_tmpl_uom.factor AS quantity,
            m.date AS date,
            m.note AS move_note,
            m.price_unit AS price_unit,
            m.origin,
            m.name AS description,
            stock_production_lot.name AS serial_number,
            'out'::text AS operation_type
        """

    def _from_stock_out(self):
        return """
        FROM
            stock_move_line as sml
        JOIN
            stock_move_svl AS m ON m.id = sml.move_id
        LEFT JOIN
            stock_production_lot ON stock_production_lot.id = sml.lot_id
        JOIN
            stock_location source_location ON sml.location_id = source_location.id
        JOIN
            stock_location dest_location ON sml.location_dest_id = dest_location.id
        JOIN
            product_product ON product_product.id = m.product_id
        JOIN
            product_template ON product_template.id = product_product.product_tmpl_id
        JOIN
            product_category AS categ ON categ.id = product_template.categ_id
        JOIN 
            uom_uom AS sml_uom ON sml_uom.id = sml.product_uom_id
        JOIN 
            uom_uom AS product_tmpl_uom ON product_tmpl_uom.id = product_template.uom_id
        LEFT JOIN
            stock_picking AS sp ON sp.id = m.picking_id
        LEFT JOIN
            stock_picking_type AS pkt ON pkt.id = m.picking_type_id
        """

    def _where_stock_out(self, company_id, stock_loc_condition, date_query, product_tmpl_query, product_query, product_categ_query):
        return """
        WHERE sml.state = 'done' AND source_location.usage in ('internal', 'transit') AND source_location.company_id = {0}
            AND (
                NOT (dest_location.company_id is null AND source_location.company_id is null) OR
                dest_location.company_id != source_location.company_id OR
                dest_location.usage NOT IN ('internal', 'transit'))
            {1}
            {2}
            {3}
            {4}
            {5}
            {6}
        """.format(company_id, stock_loc_condition, date_query, product_tmpl_query, product_query, product_categ_query, self._add_custom_filter_data())

    def _add_custom_filter_data(self):
        """
        Use: Add conditions filter data (Product moves) in stock_history.
        """
        conditions = """
        """
        return conditions

    def _get_stock_out_query(self, company_id, location_ids=[], date_from=None, date_to=None, product_tmpl_id=None, product_id=None, product_categ_id=None):
        stock_loc_condition = ""
        if len(location_ids) > 1:
            stock_loc_condition = " AND source_location.id IN {0}".format(location_ids)
        elif len(location_ids) == 1:
            stock_loc_condition = " AND source_location.id = {0}".format(location_ids[0])

        date_query = self._get_date_condition(date_from=date_from, date_to=date_to)
        product_tmpl_query = self._get_product_template_condition(product_tmpl_id)
        product_query = self._get_product_condition(product_id)
        product_categ_query = self._get_product_category_condition(product_categ_id)
        sql = """
                {0}
                {1}
                {2}
        """.format(
            self._select_stock_out(),
            self._from_stock_out(),
            self._where_stock_out(company_id, stock_loc_condition, date_query, product_tmpl_query, product_query, product_categ_query)
            )
        return sql

    #---------------------------------
    # STOCK HISTORY
    #---------------------------------
    def _select_stock_history(self):
        return """
        SELECT MIN(sh.id) AS id,
            sh.move_id,
            sh.picking_id,
            sh.picking_type_id,
            sh.location_id,
            sh.counter_location_id,
            sh.company_id,
            sh.product_id,
            sh.product_categ_id,
            sh.product_template_id,
            SUM(sh.quantity) AS quantity,
            SUM(SUM(sh.quantity)) OVER (ORDER BY sh.date ASC, sh.move_id ASC) AS commulative_qty, -- commulative quantiy of the dataset at the corresponding move
            sh.date,
            sh.move_note,
            COALESCE(SUM(sh.price_unit * sh.quantity) / NULLIF(SUM(sh.quantity), 0), 0) AS price_unit,
            SUM(COALESCE(SUM(sh.price_unit * sh.quantity), 0)) OVER (ORDER BY sh.date ASC, sh.move_id ASC) AS commulative_value, -- commulative stock value of the dataset at the corresponding move
            sh.origin,
            sh.description,
            STRING_AGG(DISTINCT sh.serial_number, ', ' ORDER BY sh.serial_number) AS serial_number,
            sh.operation_type
        """

    def _from_stock_history(self, company_id, location_ids=[], date_from=None, date_to=None, product_tmpl_id=None, product_id=None, product_categ_id=None, operation_type=None):
        stock_in_history = self._get_stock_in_query(company_id, location_ids, date_from, date_to, product_tmpl_id, product_id, product_categ_id)
        stock_out_hitory = self._get_stock_out_query(company_id, location_ids, date_from, date_to, product_tmpl_id, product_id, product_categ_id)

        if operation_type == 'in':
            foo = """({0})""".format(stock_in_history)
        elif operation_type == 'out':
            foo = """({0})""".format(stock_out_hitory)
        else:
            foo = """
                ((
                {0}
                )
                UNION ALL
                (
                {1}
                ))
            """.format(stock_in_history, stock_out_hitory)
        return """
        FROM
            (WITH stock_move_svl AS(
            {0}
            )
            {1}) AS sh""".format(self._get_stock_move_svl_query(), foo)

    def _group_by_stock_history(self):
        return """
        GROUP BY
            sh.move_id,
            sh.location_id,
            sh.company_id,
            sh.product_id,
            sh.product_categ_id,
            sh.date,
            sh.origin,
            sh.description,
            sh.product_template_id,
            sh.picking_type_id,
            sh.counter_location_id,
            sh.picking_id,
            sh.operation_type,
            sh.move_note
        """

    def get_stock_history_query(self, company_id, location_ids=[], date_from=None, date_to=None, product_tmpl_id=None, product_id=None, product_categ_id=None, operation_type=None):
        stock_history = """
                {0}
                {1}
                {2}
        """.format(
            self._select_stock_history(),
            self._from_stock_history(company_id, location_ids, date_from, date_to, product_tmpl_id, product_id, product_categ_id, operation_type),
            self._group_by_stock_history()
            )
        return stock_history

    @api.model
    def get_balance_at_date(self, product_id, company_id, date, location_ids=[]):
        """
        @param product_id: the id of the product
        @type product_id: integer
        @param company_id: the id of the company
        @type company_id: integer
        @param company_id: the datetime upto which the balance is
        @type company_id: datetime string
        @param location_ids: list of location ids
        @type location_ids: list
        @return: dictionary of qty and value {'qty': qty, 'value': value}
        @rtype: dict
        """
        tmp_tbl = self.get_stock_history_query(company_id, location_ids, date_to=date, product_id=product_id)
        sql = """
        WITH tmp_tbl AS (%s)
        SELECT SUM(quantity) AS qty,
        SUM(quantity * price_unit) AS value
        FROM tmp_tbl
        WHERE date < %s
            AND product_id = %s
        """
        self.env.cr.execute(sql, (AsIs(tmp_tbl), date, product_id))
        balance = self.env.cr.dictfetchone()
        return balance
