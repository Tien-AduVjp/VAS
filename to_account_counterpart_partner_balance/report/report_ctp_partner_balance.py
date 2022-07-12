from odoo import models, api, fields
from odoo import tools


class ReportCtpPartnerBalance(models.Model):
    _name = 'report.ctp.partner.balance'
    _description = 'Counterpart Partner Balance Report'
    _order = 'aml_id, date_maturity DESC, date DESC, partner_id, id'
    _auto = False

    aml_id = fields.Many2one('account.move.line', string='Journal Item', readonly=True)
    account_id = fields.Many2one('account.account', string='Account', readonly=True)
    account_move_id = fields.Many2one('account.move', string='Journal Entry', readonly=True)
    invoice_id = fields.Many2one('account.invoice', string='Invoice', readonly=True)
    type = fields.Selection([
        ('receivable', 'Receivable'),
        ('payable', 'Payable')], string='Type', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Partner', readonly=True)
    date = fields.Date(string='Date', help="Date of the transaction", readonly=True)
    date_maturity = fields.Date(string="Maturity", readonly=True)
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=True)
    amount_due = fields.Monetary('Due Amount', readonly=True)
    taxes = fields.Char(string='Taxes', readonly=True)
    tax_amount_due = fields.Monetary('Due Tax Amount', readonly=True)
    total_due = fields.Monetary(string='Total Due', readonly=True)
    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, readonly=True)
    state = fields.Selection([('draft', 'Unposted'), ('posted', 'Posted')], string='Status', readonly=True)

    def _due_lines_select(self):
        return """
                SELECT row_number() OVER() AS id,
                        l.id AS aml_id,
                        m.id AS account_move_id,
                        acc.id AS account_id,
                        CASE WHEN l.currency_id IS NOT NULL
                            THEN l.currency_id
                            ELSE l.company_currency_id
                            END AS currency_id,
                        CASE WHEN l.currency_id IS NOT NULL
                            THEN CASE WHEN l.countered_amt_currency <> 0.0
                                THEN -1 * (l.amount_currency - l.amount_currency * m.matched_percentage) * ctp.countered_amt_currency/l.countered_amt_currency
                                ELSE -1 * (l.amount_currency - l.amount_currency * m.matched_percentage)
                                END
                            ELSE CASE WHEN l.countered_amt <> 0.0
                                THEN -1 * (l.balance - l.balance_cash_basis) * ctp.countered_amt/l.countered_amt
                                ELSE -1 * (l.balance - l.balance_cash_basis)
                                END
                            END AS amount_due,
                        CASE WHEN l.currency_id IS NOT NULL
                            THEN CASE WHEN l.countered_amt_currency <> 0.0
                                THEN -1 * l.amount_currency * ctp.countered_amt_currency/l.countered_amt_currency
                                ELSE -1 * l.amount_currency
                                END
                            ELSE CASE WHEN l.countered_amt <> 0.0
                                THEN -1 * l.balance * ctp.countered_amt/l.countered_amt
                                ELSE -1 * l.balance
                                END
                            END AS amount_org,
                        l.date AS date,
                        l1.date_maturity AS date_maturity,
                        l.partner_id,
                        prod.id AS product_id,
                        at1.type,
                        com.id AS company_id,
                        m.state AS state
        """

    def _due_lines_from(self):
        return """
                    FROM account_move_line AS l
        """

    def _due_lines_join(self):
        return """
                        JOIN account_move AS m ON m.id = l.move_id
                        JOIN account_account AS acc ON acc.id = l.account_id
                        JOIN account_account_type at ON l.user_type_id = at.id
                        JOIN account_move_line_ctp AS ctp ON ctp.cr_aml_id = l.id OR ctp.dr_aml_id = l.id
                        JOIN account_move_line AS l1 ON l1.id = ctp.dr_aml_id OR l1.id = ctp.cr_aml_id
                        JOIN account_account_type at1 ON l1.user_type_id = at1.id
                        LEFT JOIN res_currency AS cur ON cur.id = l.currency_id
                        LEFT JOIN res_company AS com ON com.id = l.company_id
                        LEFT JOIN res_currency AS com_cur ON com_cur.id = com.currency_id AND com_cur.id = l.company_currency_id

                        LEFT JOIN product_product AS prod ON prod.id = l.product_id
        """

    def _due_lines_where(self):
        return """
                    WHERE at.type not in ('liquidity','receivable','payable')
                        AND l1.full_reconcile_id IS NULL
                        AND at1.type in ('receivable','payable')
                        /* We don't want lines with Originator Tax. We already process it among the lines with taxes */
                        AND l.tax_line_id IS NULL
        """

    def _due_lines_group_by(self):
        return """
                    GROUP BY
                        m.id,
                        l.id,
                        ctp.id,
                        l1.id,
                        com.id,
                        cur.id,
                        com_cur.id,
                        at1.id,
                        prod.id,
                        acc.id
        """

    def _get_due_lines(self):
        return """
        %s
        %s
        %s
        %s
        %s
        """ % (self._due_lines_select(), self._due_lines_from(), self._due_lines_join(), self._due_lines_where(), self._due_lines_group_by())

    def _pb_select(self):
        return """
            WITH due_line AS (%s)
            SELECT dl.id,
                dl.aml_id,
                dl.account_move_id,
                dl.account_id,
                dl.currency_id,
                dl.amount_due,
                dl.amount_org,
                CASE WHEN dl.amount_org <> 0.0
                    THEN (dl.amount_due * 100 / dl.amount_org)
                    ELSE 0.0
                END AS due_percentage,
                string_agg(tax.name, ', ') AS taxes,
                SUM(CASE WHEN tax.amount_type = 'fixed'
                        THEN tax.amount * (dl.amount_due * 100 / dl.amount_org) / 100
                        ELSE CASE WHEN (tax.amount_type = 'percent' AND tax.price_include = False) OR (tax.amount_type = 'division' AND tax.price_include = True)
                            THEN tax.amount * dl.amount_due / 100
                            ELSE CASE WHEN (tax.amount_type = 'percent' AND tax.price_include = True)
                                THEN dl.amount_due - dl.amount_due / (1 + tax.amount / 100)
                                ELSE CASE WHEN (tax.amount_type = 'division' AND tax.price_include = False)
                                    THEN dl.amount_due / (1 - tax.amount / 100) - dl.amount_due
                                    ELSE 0.0
                                    END
                                END
                            END
                        END) AS tax_amount_due,
                dl.date,
                dl.date_maturity,
                dl.partner_id,
                dl.product_id,
                dl.type,
                dl.company_id,
                dl.state
        """ % (self._get_due_lines())

    def _pb_from(self):
        return """
            FROM due_line AS dl
        """

    def _pb_join(self):
        return """
            LEFT JOIN account_move_line_account_tax_rel AS rel ON rel.account_move_line_id = dl.aml_id
            LEFT JOIN account_tax AS tax ON tax.id = rel.account_tax_id
        """

    def _pb_group_by(self):
        return """
            GROUP BY dl.id,
                dl.aml_id,
                dl.account_move_id,
                dl.account_id,
                dl.currency_id,
                dl.date,
                dl.date_maturity,
                dl.partner_id,
                dl.product_id,
                dl.type,
                dl.company_id,
                dl.amount_due,
                dl.amount_org,
                dl.state
        """

    def _get_partner_balance(self):
        return """
        %s
        %s
        %s
        %s
        """ % (self._pb_select(), self._pb_from(), self._pb_join(), self._pb_group_by())

    def _select(self):
        return """
        WITH partner_balance AS (%s)
        SELECT pb.id AS id,
            pb.aml_id,
            pb.account_move_id,
            pb.account_id,
            pb.currency_id,
            pb.amount_due,
            pb.amount_org,
            pb.due_percentage,
            pb.taxes,
            pb.tax_amount_due,
            (pb.amount_due + pb.tax_amount_due) AS total_due,
            pb.date,
            pb.date_maturity,
            pb.partner_id,
            pb.product_id,
            pb.type,
            pb.company_id,
            inv.id AS invoice_id,
            pb.state AS state
        """ % (self._get_partner_balance(),)

    def _from(self):
        return """
        FROM partner_balance AS pb
        """

    def _join(self):
        return """
        JOIN account_move_line AS l ON l.id = pb.aml_id
        LEFT JOIN account_invoice AS inv ON inv.id = l.invoice_id
        """

    def _where(self):
        sql = """
        WHERE pb.id IS NOT NULL
        """
        return sql

    def _prepare_sql(self):
        return """
        %s
        %s
        %s
        %s
        """ % (self._select(), self._from(), self._join(), self._where())

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        sql = """CREATE or REPLACE VIEW %s AS (
        %s
        )""" % (self._table, self._prepare_sql())
#         print(sql)
        self.env.cr.execute(sql)
