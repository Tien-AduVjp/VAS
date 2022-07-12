from odoo import tools
from odoo import api, fields, models


class StockReport(models.Model):
    _name = 'stock.report'
    _description = "Stock Report"
    _rec_name = 'id'
    _auto = False

    id = fields.Integer('', readonly=True)
    picking_type_id = fields.Many2one('stock.picking.type', string='Operation Type', readonly=True)
    reference = fields.Char(string='Reference', readonly=True)
    inventory_id = fields.Many2one('stock.inventory', string='Inventory Adjustment', readonly=True)
    picking_name = fields.Char(string='Picking Name', readonly=True)
    picking_id = fields.Many2one('stock.picking', string='Transfer Reference', readonly=True)
    date_done = fields.Datetime(string='Transfer Date', readonly=True)
    creation_date = fields.Datetime(string='Creation Date', readonly=True)
    scheduled_date = fields.Datetime(string='Expected Date', readonly=True)
    delay = fields.Float(string='Delay (Days)', readonly=True, group_operator='avg',
                         help="The time period (days) between the scheduled date and the actual transfer date.")
    cycle_time = fields.Float(string='Cycle Time (Days)', readonly=True, group_operator='avg',
                              help="The time period (days) between the creation date and the actual transfer date"
                              " (which is usually either order date or confirmation date)")
    state = fields.Selection([
        ('draft', 'New'), ('cancel', 'Cancelled'),
        ('waiting', 'Waiting Another Move'),
        ('confirmed', 'Waiting Availability'),
        ('partially_available', 'Partially Available'),
        ('assigned', 'Available'),
        ('done', 'Done')], string='Status', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Partner', readonly=True)
    picking_type_code = fields.Selection(related='picking_type_id.code', readonly=True)
    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    product_qty = fields.Float(string='Product Quantity', readonly=True)
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehourse', readonly=True)
    categ_id = fields.Many2one('product.category', string='Product Category', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', readonly=True)
    is_late = fields.Boolean(string='Is Late', readonly=True)
    is_backorder = fields.Boolean(string='Is a Backorder', readonly=True)

    @api.depends('reference', 'product_id.name')
    def name_get(self):
        return self.mapped(lambda r: (r.id, '%s - %s' % (r.reference, r.product_id.display_name)))

    def _query(self, with_clause='', fields={}, groupby='', from_clause='', where_clause=''):
        with_ = """WITH tmp_sp AS (
            SELECT
                id,
                name,
                date_done,
                date as creation_date,
                scheduled_date,
                partner_id,
                backorder_id IS NOT NULL as is_backorder,
                extract(epoch from date_trunc('day',date_done)-date_trunc('day',scheduled_date))/(24*60*60)::decimal(16,2) as delay,
                extract(epoch from date_trunc('day',date_done)-date_trunc('day',date))/(24*60*60)::decimal(16,2) as cycle_time
            FROM
                stock_picking
            GROUP BY
                id,
                name,
                date_done,
                date,
                scheduled_date,
                partner_id,
                is_backorder
            )
        """
        with_ += with_clause

        select_ = """
            sm.id as id,
            sp.name as picking_name,
            sp.date_done as date_done,
            sp.creation_date as creation_date,
            sp.scheduled_date as scheduled_date,
            sp.partner_id as partner_id,
            sp.is_backorder as is_backorder,
            sp.delay as delay,
            sp.delay > 0 as is_late,
            sp.cycle_time as cycle_time,
            spt.id as picking_type_id,
            p.id as product_id,
            sm.reference as reference,
            sm.picking_id as picking_id,
            spt.code AS picking_type_code,
            sm.inventory_id as inventory_id,
            sm.state as state,
            sm.product_qty as product_qty,
            sm.company_id as company_id,
            cat.id as categ_id,
            CASE
                WHEN (whs.id IS NOT NULL AND whd.id IS NULL) OR ls.usage = 'transit' THEN whs.id
                WHEN (whs.id IS NULL AND whd.id IS NOT NULL) OR ld.usage = 'transit' THEN whd.id
            END AS warehouse_id
        """

        for field in fields.values():
            select_ += field

        from_ = """
            stock_move sm
            LEFT JOIN tmp_sp AS sp ON sm.picking_id = sp.id
            LEFT JOIN stock_picking_type AS spt ON sm.picking_type_id = spt.id
            LEFT JOIN stock_location ls on (ls.id=sm.location_id)
            LEFT JOIN stock_location ld on (ld.id=sm.location_dest_id)
            LEFT JOIN stock_warehouse whs ON ls.parent_path like concat('%/', whs.view_location_id, '/%')
            LEFT JOIN stock_warehouse whd ON ld.parent_path like concat('%/', whd.view_location_id, '/%')
            INNER JOIN product_product AS p ON sm.product_id = p.id
            INNER JOIN product_template AS t ON p.product_tmpl_id = t.id
            INNER JOIN product_category AS cat ON t.categ_id = cat.id
            {additional_from}
        """.format(additional_from=from_clause)

        where_ = """
            WHERE t.type = 'product'
                %s
        """ % where_clause

        groupby_ = """
            sm.id,
            sm.reference,
            sm.picking_id,
            sm.inventory_id,
            sm.state,
            sm.product_qty,
            sm.company_id,
            sp.name,
            sp.date_done,
            sp.creation_date,
            sp.scheduled_date,
            sp.partner_id,
            sp.is_backorder,
            sp.delay,
            sp.cycle_time,
            spt.id,
            p.id,
            is_late,
            ls.usage,
            ld.usage,
            whs.id,
            whd.id,
            cat.id %s
        """ % (groupby)
        return "%s (SELECT %s FROM %s %s GROUP BY %s)" % (with_, select_, from_, where_, groupby_)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" % (self._table, self._query()))
