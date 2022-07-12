from odoo import fields, models


class Project(models.Model):
    _inherit = 'project.project'

    repair_fee_line_id = fields.Many2one('repair.fee', 'Repair Fee Line', readonly=True,
                                         help="Repair fee line from which the project has been created. Used for tracability.")

    def _plan_prepare_values(self):
        """
            Calculate the 4 costs that are used on Project Overview:
                . invoiced
                . to invoice
                . timesheet cost
                . total
        """

        values = super(Project, self)._plan_prepare_values()
        ro_lines = self.env['account.analytic.line'].search(values['timesheet_domain']).mapped('ro_line')
        invoice_lines = ro_lines.mapped('invoice_lines')
        currency = self.env.company.currency_id

        if ro_lines:

            sum_invoiced = 0.0
            sum_to_invoice = 0.0

            for inv_line in invoice_lines:
                amount = inv_line.price_unit * inv_line.quantity

                # CALCULATE INVOICED AMOUNT
                if inv_line.move_id.state == 'posted':
                    sum_invoiced += inv_line.currency_id._convert(
                        from_amount=amount,
                        to_currency=currency,
                        date=inv_line.move_id.invoice_date,
                        company=self.env.company,
                    )

                # CALCULATE TO-INVOICE AMOUNT - PART 1
                if inv_line.move_id.state == 'draft':
                    sum_to_invoice += inv_line.currency_id._convert(
                        from_amount=amount,
                        to_currency=currency,
                        date=fields.Date.today(),
                        company=self.env.company,
                    )

            # CALCULATE TO-INVOICE AMOUNT - PART 2
            for rol in ro_lines:
                sum_to_invoice += rol.repair_id.pricelist_id.currency_id._convert(
                    from_amount=rol.price_unit * rol.qty_to_invoice,
                    to_currency=currency,
                    date=fields.Date.today(),
                    company=self.env.company,
                )

            values['dashboard']['profit']['invoiced'] += sum_invoiced
            values['dashboard']['profit']['to_invoice'] += sum_to_invoice

            values['dashboard']['profit']['total'] = (
                values['dashboard']['profit']['invoiced'] +
                values['dashboard']['profit']['to_invoice'] +
                values['dashboard']['profit']['cost']
            )

        return values
