from odoo import models, fields, api
from odoo import tools


class VoucherReport(models.Model):
    _name = 'voucher.report'
    _description = "Vouchers Report"
    _auto = False

    name = fields.Char(string='Name', readonly=True)
    lot_id = fields.Many2one('stock.production.lot', readonly=True)
    product_id = fields.Many2one('product.product', readonly=True)
    current_stock_location_id = fields.Many2one('stock.location', readonly=True)
    value = fields.Float(string='Voucher Value', readonly=True)
    price = fields.Float(string='Sale Price')
    used_amount = fields.Float(string='Used Amount', readonly=True)
    serial = fields.Char(string='Serial of Voucher', readonly=True)
    issue_date = fields.Date(string='Issue Date', readonly=True)
    expiry_date = fields.Date(string='Expiry Date', readonly=True)
    state = fields.Selection([('new', 'New'), ('expired', 'Expired'), ('used', 'Used')], string='Status', readonly=True)
    issue_order_id = fields.Many2one('voucher.issue.order', string='Issue Order', readonly=True)
    used_date = fields.Datetime(string='Used Date', readonly=True)

    def _select(self):
        sql = """
        SELECT
            v.id AS id,
            v.name,
            v.lot_id,
            v.product_id,
            v.current_stock_location_id,
            v.value,
            v.used_amount,
            v.serial,
            v.issue_date,
            v.expiry_date,
            v.state,
            v.issue_order_id,
            v.price,
            v.used_date
        """
        return sql

    def _from(self):
        sql = """
        FROM
            voucher_voucher AS v
        """
        return sql

    def _join(self):
        sql = """
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

