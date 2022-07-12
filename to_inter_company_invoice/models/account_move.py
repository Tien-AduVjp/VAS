from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    inter_comp_invoice_id = fields.Many2one('account.move', string='Inter-Company Invoice', readonly=True, copy=False, ondelete='set null',
                                            help="Technical field to indicate the inter-company invoice of this invoice")

    def _get_inter_company(self):
        return self.partner_id._find_company()

    def button_cancel(self):
        for invoice in self.filtered(lambda inv: inv.inter_comp_invoice_id):
            inter_comp_user = invoice.partner_id._get_inter_comp_user()
            invoice.inter_comp_invoice_id.with_user(inter_comp_user.id).message_post(
                body=_("The inter-company invoice %s of the company %s was cancelled. Please contact that company to solve the issue.")
                % (invoice.name, invoice.company_id.name)
                )
        return super(AccountMove, self).button_cancel()

    def action_post(self):
        """ Validated invoice generate cross invoice base on company rules """
        for invoice in self:
            # do not consider invoices that have already been auto-generated, nor the invoices that were already validated in the past
            if not invoice.is_invoice():
                continue
            company = invoice._get_inter_company()
            if company and not invoice.inter_comp_invoice_id:
                invoice._generate_inter_comp_invoice()
        return super(AccountMove, self).action_post()

    def _generate_inter_comp_invoice(self):
        """
        generate an invoice for the given company: it wil copy the invoice lines in the new
        invoice. The intercompany user is the author of the new invoice.
        """
        self.ensure_one()
        company = self._get_inter_company()
        if not company:
            return self.env['account.move']

        # find user for creating the invoice from company
        inter_comp_user = self.partner_id._get_inter_comp_user()
        context = self._context.copy()
        if company.id not in context.get('allowed_company_ids',[]):
            if not context.get('allowed_company_ids',False):
                context['allowed_company_ids'] = []
            context['allowed_company_ids'].append(company.id)
        # create invoice, as the intercompany user
        invoice_vals = self.with_context(context).with_company(company).sudo()._prepare_inter_comp_invoice_data()
        invoice = self.with_context(context).with_user(inter_comp_user).create([invoice_vals])

        context['journal_id'] = invoice_vals['journal_id']
        for line in self.invoice_line_ids:
            inv_line_data = line.with_context(context).sudo()._prepare_intercomp_invoice_line_data()
            inv_line_data.update({'move_id':invoice.id})
            line2 = self.env['account.move.line'].with_user(inter_comp_user.id).new(inv_line_data)
            price_unit = line.price_unit
            if line2.product_id:
                line2._onchange_product_id()
            else:
                line2.account_id = invoice.journal_id.default_account_id
            line2.tax_ids = line2._get_computed_taxes()
            line2._set_price_and_tax_after_fpos()
            line2.price_unit = price_unit
            new_vals = {k: v or False for k, v in dict(line2._cache).items()}
            line_data = line2._convert_to_write(new_vals)
            inter_comp_invoice_line_id = line.with_context(check_move_validity=False).with_user(inter_comp_user.id).create(line_data)
            if inter_comp_invoice_line_id:
                line.write({'inter_comp_invoice_line_id': inter_comp_invoice_line_id.id})
        invoice.with_context(check_move_validity=False)._onchange_currency()
        invoice.with_context(check_move_validity=False)._recompute_dynamic_lines(recompute_all_taxes=True, recompute_tax_base_amount=True)
        self.write({'inter_comp_invoice_id': invoice.id})
        return invoice

    def _get_inter_comp_invoice_type(self):
        types_map = {
            'out_invoice': 'in_invoice',
            'out_refund': 'in_refund',
            'in_invoice': 'out_invoice',
            'in_refund': 'out_refund',
            }
        return types_map.get(self.move_type)

    def _get_inter_comp_journal_type(self):
        if self.move_type in ('out_invoice', 'out_refund'):
            journal_type = 'purchase'
        elif self.move_type in ('in_invoice', 'in_refund'):
            journal_type = 'sale'
        else:
            raise UserError(_("Could not find a proper journal type for inter-company invoice generation from the invoice in type of %s")
                          % self.move_type)
        return journal_type

    def _prepare_inter_comp_invoice_data(self):
        company = self._get_inter_company()
        inv_type = self._get_inter_comp_invoice_type()
        journal_type = self._get_inter_comp_journal_type()

        journal = self.env['account.journal'].search([('type', '=', journal_type), ('company_id', '=', company.id)], limit=1)
        if not journal:
            raise UserError(_('Please define %s journal for this company: "%s" (id:%d).') % (journal_type, company.name, company.id))

        delivery_partner_id = self.company_id.partner_id.address_get(['delivery'])['delivery']
        fiscal_position_id = self.env['account.fiscal.position'].get_fiscal_position(
            self.company_id.partner_id.id, delivery_id=delivery_partner_id
        )

        context = self._context.copy()
        context['company_id'] = company.id
        vals = {'name': self.name,
            'invoice_origin': "%s %s %s" % (self.company_id.name, _('Invoice:'), self.name),
            'move_type': inv_type,
            'invoice_date': self.invoice_date,
            'ref': self.ref,
            'partner_id': self.company_id.partner_id.id,
            'journal_id': journal.id,
            'currency_id': self.currency_id and self.currency_id.id,
            'company_id': company.id,
            'inter_comp_invoice_id': self.id,
            'fiscal_position_id': fiscal_position_id,
            }
        inv = self.env['account.move'].with_context(context).new(vals)
        inv._onchange_partner_id()
        new_vals = {k: v or False for k, v in dict(inv._cache).items()}
        data = inv._convert_to_write(new_vals)
        return data
