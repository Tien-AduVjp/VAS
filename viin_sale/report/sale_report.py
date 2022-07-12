from odoo import models, fields


class SaleReport(models.Model):
    _inherit = 'sale.report'

    create_date = fields.Datetime('Creation Date', readonly=True)
    days_to_confirm = fields.Float('Days To Confirm', readonly=True,
                                   help="Number of days counting from Creation Date to Ordered Date of an order.")
    invoice_status = fields.Selection([
        ('upselling', 'Upselling Opportunity'),
        ('invoiced', 'Fully Invoiced'),
        ('to invoice', 'To Invoice'),
        ('no', 'Nothing to Invoice')
        ], string="Invoicing Status", readonly=True)

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        fields['create_date'] = ", s.create_date as create_date"
        fields['days_to_confirm'] = ", s.days_to_confirm as days_to_confirm"
        fields['invoice_status'] = ', s.invoice_status as invoice_status'

        groupby += ', s.invoice_status, s.create_date'

        return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)
