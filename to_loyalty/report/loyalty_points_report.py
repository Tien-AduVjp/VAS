from odoo import models, fields, tools


class LoyaltyPointsReport(models.Model):
    _name = 'loyalty.points.report'
    _description = "Loyalty Points Report"
    _auto = False

    name = fields.Char(string='Reference', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Customer', readonly=True)
    salesperson_id = fields.Many2one('res.users', string='Salesperson', readonly=True)
    team_id = fields.Many2one('crm.team', string='Team/Channel', readonly=True)
    loyalty_program_id = fields.Many2one('loyalty.program', string='Loyalty Program', readonly=True)
    points = fields.Float(string='Points', readonly=True)
    reward_id = fields.Many2one('loyalty.reward', string='Reward', readonly=True)
    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    product_qty = fields.Float(string='Product Quantity', readonly=True)
    price_total = fields.Float('Price Subtotal', readonly=True)
    date_order = fields.Datetime(string='Date Order', readonly=True)
    point_type = fields.Selection([('won', 'Won'), ('spent', 'Spent')], readonly=True)

    def _select(self):
        sql = """
        SELECT
            p.id AS id,
            p.name,
            p.partner_id,
            p.salesperson_id,
            p.team_id,
            p.loyalty_program_id,
            p.points,
            p.reward_id,
            p.product_id,
            p.product_qty,
            p.price_total,
            p.date_order,
            CASE
                WHEN p.points > 0 THEN 'won'::text
                ELSE 'spent'::text
                END AS point_type
        """
        return sql

    def _from(self):
        sql = """
        FROM
            loyalty_point AS p
        """
        return sql

    def _join(self):
        sql = """
        JOIN
            loyalty_program AS lp ON lp.id = p.loyalty_program_id
        LEFT JOIN
            loyalty_reward AS lr ON lr.id = p.reward_id
        JOIN
            res_partner AS partner ON partner.id = p.partner_id
        LEFT JOIN
            res_users AS u ON u.id = p.salesperson_id
        LEFT JOIN
            product_product AS pp ON pp.id = p.product_id
        LEFT JOIN
            product_template AS p_tmpl ON p_tmpl.id = pp.product_tmpl_id
        """
        return sql

    def _where(self):
        sql = """
        """
        return sql

    def _group_by(self):
        group_by_str = """
        """
        return group_by_str

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            %s
            %s
            %s
            %s
            )
        """ % (self._table, self._select(), self._from(), self._join(), self._where(), self._group_by()))
