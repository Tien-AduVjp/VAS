from odoo import tools
from odoo import fields, models


class RepairReport(models.Model):
    _name = "repair.report"
    _description = "Repair Report"
    _auto = False
    _rec_name = 'date'
    _order = 'date desc'

    name = fields.Char('Repair order', readonly=True)
    date = fields.Datetime('Repair Date', readonly=True)
    repair_id = fields.Many2one('repair.order', string='Repair Order', readonly=True)
    repair_product_id = fields.Many2one('product.product', 'Repair Product', readonly=True)
    lot_id = fields.Many2one('stock.production.lot', 'Lot/Serial', readonly=True)
    partner_id = fields.Many2one('res.partner', 'Customer', readonly=True)
    company_id = fields.Many2one('res.company', 'Company', readonly=True)
    user_id = fields.Many2one('res.users', 'Responsible', readonly=True)
    supervisor_id = fields.Many2one('res.users', 'Supervisor', readonly=True)
    price_subtotal = fields.Float('Untaxed Total', readonly=True)
    location_id = fields.Many2one('stock.location', 'Location', readonly=True)
    operation_product_id = fields.Many2one('product.product', 'Part Product', readonly=True)
    operation_product_uom_qty = fields.Float('Part Product Qty', readonly=True)
    state = fields.Selection([
        ('draft', 'Quotation'),
        ('cancel', 'Cancelled'),
        ('confirmed', 'Confirmed'),
        ('under_repair', 'Under Repair'),
        ('ready', 'Ready to Repair'),
        ('2binvoiced', 'To be Invoiced'),
        ('invoice_except', 'Invoice Exception'),
        ('done', 'Repaired'),
        ], string='Status', readonly=True)

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        with_ = ("WITH %s" % with_clause) if with_clause else ""

        select_ = """
            min(l.id) as id,
            l.product_id as operation_product_id,
            sum(l.product_uom_qty / u.factor * u2.factor) as operation_product_uom_qty,
            sum(l.price_subtotal) as price_subtotal,
            count(*) as nbr,
            t.name as name,
            r.repair_date as date,
            r.lot_id as lot_id,
            r.state as state,
            r.location_id as location_id,
            r.product_id as repair_product_id,
            r.partner_id as partner_id,
            r.user_id as user_id,
            r.supervisor_id as supervisor_id,
            r.company_id as company_id,
            r.id as repair_id
        """

        for field in fields.values():
            select_ += field

        from_ = """
                (SELECT
                    id,
                    repair_id,
                    product_id,
                    product_uom,
                    price_subtotal,
                    product_uom_qty
                    FROM repair_line
                    
                UNION ALL(

                SELECT
                    id,
                    repair_id,
                    product_id,
                    product_uom,
                    price_subtotal,
                    product_uom_qty
                    FROM repair_fee
                    )
                ) as l
                JOIN repair_order r on (l.repair_id=r.id)
                LEFT JOIN product_product p on (l.product_id=p.id)
                LEFT JOIN product_template t on (p.product_tmpl_id=t.id)
                LEFT JOIN uom_uom u on (u.id=l.product_uom)
                LEFT JOIN uom_uom u2 on (u2.id=t.uom_id)
                %s
        """ % from_clause

        groupby_ = """
            l.product_id,
            t.name,
            r.repair_date,
            r.partner_id,
            r.supervisor_id,
            r.user_id,
            r.state,
            r.company_id,
            r.id %s
        """ % (groupby)

        return '%s (SELECT %s FROM %s WHERE r.product_id IS NOT NULL GROUP BY %s)' % (with_, select_, from_, groupby_)

    def init(self):
        # self._table = sale_report
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" % (self._table, self._query()))
