from odoo import models, fields, api
from odoo import tools

class FleetVehicleCostReport(models.Model):
    _name = "fleet.vehicle.cost.report"
    _description = "Fleet Vehicle Cost Analysis"
    _auto = False

    name = fields.Char(string='Name', readonly=True)
    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle", readonly=True)
    cost_subtype_id = fields.Many2one('fleet.service.type', string="Cost Subtype", readonly=True)
    amount = fields.Float(string='Cost', readonly=True)
    cost_type = fields.Selection([('contract', 'Contract'), ('services', 'Services'), ('fuel', 'Fuel'), ('other', 'Other')], string='Cost Type', readonly=True)
    parent_id = fields.Many2one('fleet.vehicle.cost', string='Parent Cost', readonly=True)
    date = fields.Date(string='Date', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', readonly=True)
    contract_id = fields.Many2one('fleet.vehicle.log.contract', string='Contract', readonly=True)
#     currency_id = fields.Many2one('res.currency', string='Currency')

    product_id = fields.Many2one('product.product', string='Invoiceable Product', readonly=True,
                                 help="The product to be used when invoicing the vehicle cost")

    invoice_id = fields.Many2one('account.move', string='Invoice Ref.', readonly=True)

    vendor_id = fields.Many2one('res.partner', string='Vendor', readonly=True)

    def _select(self):
        select_str = """
            WITH currency_rate as (%s)
             SELECT min(c.id) as id,
                    c.product_id as product_id,
                    c.name as name,
                    c.date as date,
                    c.vehicle_id as vehicle_id,
                    p.id as vendor_id,
                    c.company_id as company_id,
                    sum(amount / COALESCE(cr.rate, 1.0)) as amount,
                    c.cost_subtype_id AS cost_subtype_id,
                    c.cost_type AS cost_type,
                    c.parent_id AS parent_id,
                    c.contract_id AS contract_id,
                    inv.id AS invoice_id
        """ % self.env['res.currency']._select_companies_rates()
        return select_str

    def _from(self):
        from_str = """
            FROM
                fleet_vehicle_cost AS c
        """
        return from_str

    def _join(self):
        join_str = """
            LEFT JOIN account_move_line AS invl ON invl.id = c.invoice_line_id
            LEFT JOIN account_move AS inv ON inv.id = invl.move_id
            LEFT JOIN res_partner AS p ON p.id = c.vendor_id
            LEFT JOIN currency_rate cr on (cr.currency_id = c.currency_id and
                        cr.company_id = c.company_id and
                        cr.date_start <= coalesce(c.date, now()) and
                        (cr.date_end is null or cr.date_end > coalesce(c.date, now())))
        """
        return join_str

    def _where(self):
        where_str = """
        WHERE ((c.created_from_invoice_line_id IS NOT NULL AND c.invoice_line_id IS NOT NULL) OR c.created_from_invoice_line_id IS NULL)
        """
        return where_str

    def _group_by(self):
        group_by_str = """
            GROUP BY
                c.product_id,
                c.name,
                c.date,
                c.vehicle_id,
                p.id,
                c.company_id,
                c.cost_subtype_id,
                c.cost_type,
                c.parent_id,
                c.contract_id,
                inv.id
        """
        return group_by_str

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE or REPLACE VIEW %s as (
                 %s
                 %s
                 %s
                 %s
                 %s
            )
        """ % (self._table, self._select(), self._from(), self._join(), self._where(), self._group_by()))
