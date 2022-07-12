from odoo import models, fields, api
from odoo import tools
import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF

class CashFlowForecastReport(models.Model):
    _name = 'cash.flow.forecast.report'
    _description = "Cash Flow Forecast Report"
    _auto = False
    _order = 'date'
    
    name = fields.Char('Reference', readonly=True)
    date = fields.Date('Date Forecast', readonly=True)
    amount = fields.Float(string='Amount', readonly=True)
    partner_id = fields.Many2one('res.partner', 'Partner', readonly=True)
    type = fields.Selection([('_a0_start_cash_balance', 'Start Cash Balance'), ('cash_in', 'Cash In'), ('cash_out', 'Cash Out')], string='Type', readonly=True)
    resource = fields.Selection([('_a0_start_cash_balance', 'Start Cash Balance'),
                                 ('account_payable', 'Account Payable'),
                                 ('account_receivable', 'Account Receivable'),
                                 ('sale_order', 'Sale Orders'),
                                 ('purchase_order', 'Purchase Order'),
                                 ('user_input', 'User Inputs')], string='Resource', readonly=True)
    
    def _get_currency_rate(self):
        return """WITH currency_rate as (%s)""" % self.env['res.currency']._select_companies_rates()
    
    def _start_cash_balance(self):
        query = """
            SELECT '(a) Start Cash Balance' AS name,
                now() AS date,
                sum(l.debit-l.credit) AS amount,
                NULL AS partner_id,
                '_a0_start_cash_balance' AS type,
                '_a0_start_cash_balance' AS resource
            FROM account_move_line l
            LEFT JOIN account_account a ON (l.account_id = a.id)
            LEFT JOIN account_move am ON (am.id=l.move_id)
            LEFT JOIN account_account_type AS act ON act.id = a.user_type_id
            WHERE am.state != 'draft' AND act.type = 'liquidity'
        """
        return query
        
    def _account_payable_query(self):
        query = """
            SELECT aml.name AS name,
                aml.date_maturity AS date,
                aml.amount_residual AS amount,
                aml.partner_id AS partner_id,
                'cash_out' AS type,
                'account_payable' AS resource
            FROM account_move_line aml
            JOIN account_account AS ac ON ac.id = aml.account_id
            WHERE aml.reconciled = False AND ac.internal_type = 'payable' AND aml.credit > 0.0
        """
        return query
    
    def _account_receivable_query(self):
        query = """
            SELECT aml.name AS name,
                aml.date_maturity AS date,
                aml.amount_residual AS amount,
                aml.partner_id AS partner_id,
                'cash_in' AS type,
                'account_receivable' AS resource
            FROM account_move_line aml
            JOIN account_account AS ac ON ac.id = aml.account_id
            WHERE aml.reconciled = False AND ac.internal_type = 'receivable' AND aml.debit > 0.0
        """
        return query
    
#     def _sale_order_line_query(self):
#         query = """
#             SELECT so.name AS name,
#                 so.confirmation_date AS date,
#                 (sol.qty_to_invoice * price_unit) / COALESCE (cr.rate, 1.0) AS amount,
#                 so.partner_id AS partner_id,
#                 'cash_in' AS type,
#                 'sale_order' AS resource
#             FROM 
#                 sale_order_line sol
#                 JOIN sale_order so ON (so.id = sol.order_id)
#                 LEFT JOIN product_pricelist pp ON (pp.id = so.pricelist_id)
#                 LEFT JOIN currency_rate cr ON (cr.currency_id = pp.currency_id AND
#                         cr.company_id = so.company_id AND
#                         cr.date_start <= COALESCE(so.date_order, now()) AND
#                         (cr.date_end IS NULL OR cr.date_end > COALESCE(so.date_order, now())))
#             WHERE so.state in ('sale', 'done') AND sol.qty_to_invoice > 0.0
#         """
#         return query
#     
#     def _purchase_order_line_query(self):
#         query = """
#             SELECT po.name AS name,
#                 po.date_planned AS date,
#                 ((-1) * (pol.product_qty - pol.qty_invoiced) * price_unit) / COALESCE (cr.rate, 1.0) AS amount,
#                 po.partner_id AS partner_id,
#                 'cash_out' AS type,
#                 'purchase_order' AS resource
#             FROM 
#                 purchase_order_line pol
#                 JOIN purchase_order po ON (po.id = pol.order_id)
#                 LEFT JOIN currency_rate cr on (cr.currency_id = po.currency_id and
#                     cr.company_id = po.company_id and
#                     cr.date_start <= coalesce(po.date_order, now()) and
#                     (cr.date_end is null or cr.date_end > coalesce(po.date_order, now())))
#             WHERE po.state in ('purchase', 'done') AND pol.qty_invoiced < pol.product_qty
#         """
#         return query
    
    def _user_input_query(self):
        query = """
            SELECT cf.name AS name,
                cf.date AS date,
                CASE 
                    WHEN cf.type = 'cash_in' THEN cf.amount / COALESCE (cr.rate, 1.0)
                    WHEN cf.type = 'cash_out' THEN (-1) * cf.amount / COALESCE (cr.rate, 1.0)
                    END AS amount,
                cf.partner_id AS partner_id,
                cf.type AS type,
                'user_input' AS resource
            FROM 
                cash_flow_user_input cf
                LEFT JOIN currency_rate cr on (cr.currency_id = cf.currency_id and
                    cr.company_id = cf.company_id and
                    cr.date_start <= coalesce(cf.date, now()) and
                    (cr.date_end is null or cr.date_end > coalesce(cf.date, now())))
            WHERE cf.state = 'confirm'
        """
        return query
        
    def _get_default_cash_flow(self):
        query = """
            WITH default_cash_flow AS (%s %s UNION ALL %s UNION ALL %s UNION ALL %s)
        """ % (self._get_currency_rate(), self._start_cash_balance(), self._account_payable_query(), self._account_receivable_query(), self._user_input_query())
        return query
    
    def _get_full_cash_flow(self):
        query = """
            %s
                SELECT EXTRACT(YEAR FROM date) AS year, EXTRACT(MONTH FROM date) AS month 
                FROM default_cash_flow 
                WHERE date >= now()
                GROUP BY year, month 
                ORDER BY year, month
        """ % (self._get_default_cash_flow())
        self.env.cr.execute(query)
        results = self.env.cr.dictfetchall()
        query_str = """
            WITH full_cash_flow AS(
            %s
            
        """ % (self._get_default_cash_flow())
        i = 0
        for line in results[1:]:
            date = datetime.date(int(line.get('year')), int(line.get('month')), 1).strftime(DF)
            if i != 0:
                query_str += """ UNION ALL"""
            query_str += """ SELECT '(a) Start Cash Balance' AS name,
                                            to_date('%s', 'YYYY-MM-DD') AS date,
                                            sum(amount) AS amount,
                                            0 AS partner_id,
                                            '_a0_start_cash_balance' AS type,
                                            '_a0_start_cash_balance' AS resource
                                        FROM default_cash_flow
                                        WHERE date < '%s'
            """ % (date, date)
            i += 1
        if i > 0:
            query_str += """ UNION ALL"""
        query_str += """ SELECT name, date, amount, partner_id, type, resource FROM default_cash_flow WHERE date >= now()"""
        query_str += """ UNION ALL SELECT '(b) Overdue amount' AS name,
                                            now() AS date,
                                            sum(amount) AS amount,
                                            0 AS partner_id,
                                            '_a0_start_cash_balance' AS type,
                                            '_a0_start_cash_balance' AS resource
                                        FROM default_cash_flow
                                        WHERE date < now())
        """
        return query_str
    
    def _final_query(self):
        select_str = """
            %s
            SELECT ROW_NUMBER() OVER() AS id,
                    name,
                    DATE(date),
                    amount,
                    partner_id,
                    type,
                    resource
            FROM full_cash_flow
        """ % self._get_full_cash_flow()
        return select_str
    
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            )
        """ % (self._table, self._final_query()))
        
        
        
