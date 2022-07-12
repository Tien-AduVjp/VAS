from datetime import datetime

from odoo import models, api


class PersonalSalesTarget(models.Model):
    _inherit = 'personal.sales.target'

    def _get_sales_orders(self):
        self.ensure_one()
        start_date = datetime.combine(self.start_date, datetime.min.time())
        end_date = datetime.combine(self.end_date, datetime.max.time())
        return self.sale_person_id.st_sales_order_ids.filtered(lambda o: o.date_order >= start_date \
                                                               and o.date_order <= end_date \
                                                               and o.team_id == self.crm_team_id)

    @api.depends('sale_person_id.st_sales_order_ids', 'sale_person_id.st_sales_order_ids.state', 'state')
    def _compute_sale_order_ids(self):
        return super(PersonalSalesTarget, self)._compute_sale_order_ids()

    def _get_sale_report_domain(self):
        self.ensure_one()
        return [
            ('order_id', 'in', self.sale_order_ids.ids),
            ('user_id', '=', self.sale_person_id.id),
            ('team_id', '=', self.crm_team_id.id),
            ('date', '>=', self.start_date),
            ('date', '<=', self.end_date),
            ('state', 'in', ('sale', 'done'))
            ]

    def _get_sales_invoices(self):
        return self.sale_person_id.st_sales_invoice_ids.filtered(lambda inv: inv.invoice_date >= self.start_date \
                                                                 and inv.invoice_date <= self.end_date \
                                                                 and inv.team_id == self.crm_team_id)

    @api.depends('sale_person_id.st_sales_invoice_ids', 'sale_person_id.st_sales_invoice_ids.state', 'state')
    def _compute_sales_invoice_ids(self):
        return super(PersonalSalesTarget, self)._compute_sales_invoice_ids()

    def _get_sales_invoices_domain(self):
        self.ensure_one()
        return [
            ('move_id', 'in', self.sales_invoice_ids.ids),
            ('invoice_user_id', '=', self.sale_person_id.id),
            ('team_id', '=', self.crm_team_id.id),
            ('invoice_date', '>=', self.start_date),
            ('invoice_date', '<=', self.end_date),
            ('move_type', 'in', ('out_invoice', 'out_refund')),
            ('state', '=', 'posted')]
