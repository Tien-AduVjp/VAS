from odoo import api, fields, models, tools


class AssetAssetReport(models.Model):
    _name = "asset.asset.report"
    _description = "Assets Analysis"
    _auto = False

    name = fields.Char(string='Year', required=False, readonly=True)
    date = fields.Date(readonly=True)
    depreciation_date = fields.Date(string='Depreciation Date', readonly=True)
    asset_id = fields.Many2one('account.asset.asset', string='Asset', readonly=True)
    asset_category_id = fields.Many2one('account.asset.category', string='Asset category', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Partner', readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'), ('open', 'Running'), ('close', 'Close'),
        ('stock_in', 'Stock-In'), ('sold', 'Sold'), ('disposed', 'Disposed')], string='Status', readonly=True)
    depreciation_value = fields.Float(string='Amount of Depreciation Lines', readonly=True)
    installment_value = fields.Float(string='Amount of Installment Lines', readonly=True)
    move_check = fields.Boolean(string='Posted', readonly=True)
    installment_nbr = fields.Integer(string='Installment Count', readonly=True)
    depreciation_nbr = fields.Integer(string='Depreciation Count', readonly=True)
    gross_value = fields.Float(string='Gross Amount', readonly=True)
    posted_value = fields.Float(string='Posted Amount', readonly=True)
    unposted_value = fields.Float(string='Unposted Amount', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', readonly=True)
    active = fields.Boolean(string='Active', readonly=True)

    def _select(self):
        select_str = """
             SELECT min(dl.id) as id,
                    dl.name as name,
                    dl.depreciation_date as depreciation_date,
                    a.active as active,
                    a.date as date,
                    (CASE WHEN dlmin.id = min(dl.id)
                      THEN a.value
                      ELSE 0
                      END) as gross_value,
                    dl.amount as depreciation_value,
                    dl.amount as installment_value,
                    (CASE WHEN dl.move_check AND move.state = 'posted'
                      THEN dl.amount
                      ELSE 0
                      END) as posted_value,
                    dl.asset_id as asset_id,
                    dl.move_check as move_check,
                    a.category_id as asset_category_id,
                    a.partner_id as partner_id,
                    a.state as state,
                    (CASE WHEN NOT dl.move_check OR move.state != 'posted'
                      THEN dl.amount
                      ELSE 0
                      END) as unposted_value,
                    count(dl.*) as installment_nbr,
                    count(dl.*) as depreciation_nbr,
                    a.company_id as company_id
        """
        return select_str

    def _from(self):
        from_str = """
            FROM account_asset_depreciation_line dl
                    left join account_asset_asset a on (dl.asset_id=a.id)
                    left join account_move move on (dl.move_id=move.id)
                    left join (select min(d.id) as id, ac.id as ac_id 
                    from account_asset_depreciation_line as d inner join account_asset_asset as ac ON (ac.id=d.asset_id) 
                    group by ac_id) as dlmin on dlmin.ac_id=a.id
        """
        return from_str

    def _group_by(self):
        group_by_str = """
            GROUP BY dl.amount,dl.asset_id,dl.depreciation_date,dl.name,
                    a.date, dl.move_check, move.state, a.state, a.category_id, a.partner_id, a.company_id,
                    a.value, a.id, a.salvage_value, dlmin.id
        """
        return group_by_str

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (%s %s %s)""" % 
                            (self._table, self._select(), self._from(), self._group_by()))
