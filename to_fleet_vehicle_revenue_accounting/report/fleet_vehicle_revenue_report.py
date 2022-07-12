from odoo import models, fields
from odoo import tools


class FleetVehicleRevenueReport(models.Model):
    _name = "fleet.vehicle.revenue.report"
    _description = "Fleet Vehicle Revenue Analysis"
    _auto = False

    name = fields.Char(string='Name', readonly=True)
    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle", readonly=True)
    revenue_subtype_id = fields.Many2one('fleet.service.type', string="Revenue Subtype", readonly=True)
    amount = fields.Float(string='Revenue', readonly=True)
    revenue_type = fields.Selection([('contract', 'Contract'), ('services', 'Services'), ('fuel', 'Fuel'), ('other', 'Other')], string='Revenue Type', readonly=True)
    date = fields.Date(string='Date', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', readonly=True)
#     currency_id = fields.Many2one('res.currency', string='Currency')

    product_id = fields.Many2one('product.product', string='Invoiceable Product', readonly=True,
                                 help="The product to be used when invoicing the vehicle revenue")

    move_id = fields.Many2one('account.move', string='Invoice Ref.', readonly=True)

    customer_id = fields.Many2one('res.partner', string='Customer', readonly=True)

    state = fields.Selection([
        ('not_invoiced', 'Not Invoiced'),
        ('invoiced_not_paid', 'Invoiced but Not Paid'),
        ('invoiced_paid', 'Invoiced and Paid'),
        ], string='Status', readonly=True)
    communication = fields.Char(string='Communication', help="This field holds the name value of either the invoiceable"
                                " product or the revenue sub-type (in case of no product specified)", readonly=True)

    def _select(self):
        select_str = """
        WITH currency_rate as (%s)
            SELECT min(r.id) as id,
                r.product_id as product_id,
                r.name as name,
                r.date as date,
                r.vehicle_id as vehicle_id,
                p.id as customer_id,
                r.company_id as company_id,
                sum(amount / COALESCE(cr.rate, 1.0)) as amount,
                r.revenue_subtype_id AS revenue_subtype_id,
                r.revenue_type AS revenue_type,
                inv.id AS move_id,
                CASE WHEN r.invoice_line_id IS NULL
                    THEN 'not_invoiced'
                    ELSE
                        CASE WHEN inv.state != 'paid'
                            THEN 'invoiced_not_paid'
                            ELSE 'invoiced_paid'
                        END
                    END AS state,
                CASE WHEN r.product_id IS NOT NULL
                    THEN
                        CASE WHEN attval.name IS NOT NULL
                            THEN CONCAT_WS('', concat_ws(' (', tmpl.name, attval.name), ')')
                            ELSE tmpl.name
                        END
                    ELSE subtype.name
                    END AS communication
        """ % self.env['res.currency']._select_companies_rates()
        return select_str

    def _from(self):
        from_str = """
            FROM
                fleet_vehicle_revenue AS r
        """
        return from_str

    def _join(self):
        join_str = """
            LEFT JOIN account_move_line AS invl ON invl.id = r.invoice_line_id
            LEFT JOIN account_move AS inv ON inv.id = invl.move_id
            LEFT JOIN res_partner AS p ON p.id = r.customer_id
            LEFT JOIN currency_rate cr on (cr.currency_id = r.currency_id and
                        cr.company_id = r.company_id and
                        cr.date_start <= coalesce(r.date, now()) and
                        (cr.date_end is null or cr.date_end > coalesce(r.date, now())))

            LEFT JOIN fleet_service_type AS subtype ON subtype.id = r.revenue_subtype_id

            LEFT JOIN product_product AS prod ON prod.id =  r.product_id
            LEFT JOIN product_template AS tmpl ON tmpl.id = prod.id

            LEFT JOIN product_attribute_product_template_rel AS valprel ON valprel.product_template_id = tmpl.id
            LEFT JOIN product_attribute_value AS attval ON attval.attribute_id = valprel.product_attribute_id
            LEFT JOIN product_attribute AS att ON att.id = valprel.product_attribute_id
            LEFT JOIN product_attribute_value_product_template_attribute_line_rel AS attlinevalrel ON attlinevalrel.product_attribute_value_id = attval.id
            LEFT JOIN product_template_attribute_line AS attline ON attline.attribute_id = att.id
        """
        return join_str

    def _where(self):
        where_str = """
        WHERE ((r.created_from_invoice_line_id IS NOT NULL AND r.invoice_line_id IS NOT NULL)
            OR r.created_from_invoice_line_id IS NULL)
        """
        return where_str

    def _group_by(self):
        group_by_str = """
            GROUP BY
                r.product_id,
                r.name,
                r.date,
                r.vehicle_id,
                p.id,
                r.company_id,
                r.revenue_subtype_id,
                r.revenue_type,
                inv.id,
                r.invoice_line_id,
                attval.id,
                tmpl.id,
                subtype.id
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
