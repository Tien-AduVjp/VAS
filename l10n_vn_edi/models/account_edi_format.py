import base64

from odoo import models, fields
from odoo.tests.common import Form
from odoo.tools import float_round


class AccountEdiFormat(models.Model):
    _inherit = 'account.edi.format'

    def _is_embedding_to_invoice_pdf_needed(self):
        # OVERRIDE
        self.ensure_one()
        return True if self.code == 'edi_vn_xml' else super()._is_embedding_to_invoice_pdf_needed()

    def _get_embedding_to_invoice_pdf_values(self, invoice):
        values = super()._get_embedding_to_invoice_pdf_values(invoice)
        if values and self.code == 'edi_vn_xml':
            values['name'] = 'edi_vn.xml'
        return values

    def _retrieve_uom(self, name):
        return self.env['uom.uom'].search([('name', 'ilike', name)], limit=1)

    def _is_e_vn(self, filename, tree):
        return self.code == 'edi_vn_xml' and tree.tag == '{http://laphoadon.gdt.gov.vn/2014/09/invoicexml/v1}invoice'

    ####################################################
    # Export Invoice
    ####################################################
    def _post_invoice_edi(self, invoices, test_mode=False):
        self.ensure_one()
        if self.code != 'edi_vn_xml':
            return super()._post_invoice_edi(invoices, test_mode=test_mode)
        res = {}
        for invoice in invoices:
            try:
                attachment = self._export_e_vn(invoice)
                res[invoice] = {'attachment': attachment}
            except Exception as e:
                res[invoice] = {'error': e}
        return res

    def _export_e_vn(self, invoice):
        self.ensure_one()
        # Create file content.
        template_values = {
            'invoice': invoice,
            'company': invoice.company_id,
            'partner': invoice.partner_id,
            'exchangeRate': float_round((1 / invoice.currency_id.with_context(date=invoice.invoice_date).rate),
                                        precision_digits=4),
            'invoice_lines': [],
            'tax_lines': []
        }
        invoice_line_values = invoice.with_context(edi_vn_xml=True).invoice_line_ids._prepare_einvoice_lines_data()
        if invoice_line_values:
            template_values.update({'invoice_lines': invoice_line_values})

        tax_lines = []
        exemption_group = self.env.ref('l10n_vn_common.account_tax_group_exemption').id
        invoice_tax = invoice._prepare_invoice_tax_data()

        for tax_line in invoice_tax:
            if tax_line['tax_group_id'] == exemption_group:
                tax_lines.append({
                    'vatPercentage': -2,
                    'vatTaxableAmount': tax_line['amount'],
                    'vatTaxAmount': 0
                })
            else:
                tax_lines.append({
                    'vatPercentage': tax_line['percent'],
                    'vatTaxableAmount': tax_line['amount'],
                    'vatTaxAmount': tax_line['amount_tax']
                })
        if tax_lines:
            template_values.update({'tax_lines': tax_lines})
        xml_content = b"<?xml version='1.0' encoding='UTF-8'?>"
        xml_content += self.env.ref('l10n_vn_edi.vn_einvoice_templates')._render(template_values)
        xml_name = '%s_edi_vn.xml' % (invoice.name.replace('/', '_'))
        return self.env['ir.attachment'].create({
            'name': xml_name,
            'datas': base64.encodebytes(xml_content),
            'mimetype': 'application/xml'
        })

    ####################################################
    # Create invoice
    ####################################################
    def _create_invoice_from_xml_tree(self, filename, tree, journal=None):
        self.ensure_one()
        if self._is_e_vn(filename, tree):
            return self._create_invoice_from_e_vn(tree)
        return super()._create_invoice_from_xml_tree(filename, tree, journal)

    def _create_invoice_from_e_vn(self, tree):
        invoice = self.env['account.move']
        journal = invoice._get_default_journal()
        move_type = 'out_invoice' if journal.type == 'sale' else 'in_invoice'
        invoice = invoice.with_context(default_move_type=move_type, default_journal_id=journal.id)
        return self._import_e_vn(tree, invoice)

    ####################################################
    # Update invoice
    ####################################################
    def _update_invoice_from_xml_tree(self, filename, tree, invoice):
        self.ensure_one()
        if self._is_e_vn(filename, tree):
            return self._update_invoice_from_e_vn(tree, invoice)
        return super()._update_invoice_from_xml_tree(filename, tree, invoice)

    def _update_invoice_from_e_vn(self, tree, invoice):
        invoice = invoice.with_context(default_move_type=invoice.move_type, default_journal_id=invoice.journal_id.id)
        return self._import_e_vn(tree, invoice)

    def _import_e_vn(self, tree, invoice):
        """ Decodes an E-invoice into an invoice."""
        namespaces = tree.nsmap

        def _find_value(xpath, element=tree):
            return self._find_value(xpath, element, namespaces)

        with Form(invoice.with_context(account_predictive_bills_disable_prediction=True)) as invoice_form:
            self_ctx = self.with_company(invoice.company_id.id)

            # Partner
            if invoice_form.journal_id.type == 'purchase':
                invoice_form.partner_id = self_ctx._retrieve_partner(
                    name=_find_value('//inv:sellerLegalName'),
                    phone=_find_value('//inv:sellerPhoneNumber'),
                    mail=_find_value('//inv:sellerEmail'),
                    vat=_find_value('//inv:sellerTaxCode'),
                )
            else:
                invoice_form.partner_id = self_ctx._retrieve_partner(
                    name=_find_value('//inv:buyerLegalName'),
                    mail=_find_value('//inv:buyerEmail'),
                    vat=_find_value('//inv:buyerTaxCode'),
                )

            # Reference.
            result = _find_value('//inv:invoiceNumber')
            if result:
                invoice_form.ref = result
                invoice_form.legal_number = result

            # Dates
            result = _find_value('//inv:invoiceIssuedDate')
            if result:
                invoice_form.invoice_date = fields.Date.to_date(result)

            # Currency
            result = _find_value('//inv:currencyCode')
            if result:
                currency = self.env['res.currency'].search([('name', '=', result.upper())], limit=1)
                invoice_form.currency_id = currency

            # Lines
            elements = tree.xpath('//inv:item', namespaces=namespaces)
            if elements:
                for element in elements:
                    with invoice_form.invoice_line_ids.new() as invoice_line_form:
                        # Display Type
                        selection = _find_value('.//inv:selection', element)
                        if selection and selection == 2:
                            invoice_line_form.display_type = 'line_note'

                        # Sequence.
                        line_elements = _find_value('.//inv:lineNumber', element)
                        if line_elements:
                            invoice_line_form.sequence = int(line_elements)

                        # Product.
                        name = _find_value('.//inv:itemName', element)
                        invoice_line_form.product_id = self_ctx._retrieve_product(
                            default_code=_find_value('.//inv:itemCode', element),
                            name=name,
                        )
                        if name:
                            invoice_line_form.name = name

                        # Quantity.
                        line_elements = _find_value('.//inv:quantity', element)
                        if line_elements:
                            invoice_line_form.quantity = float(line_elements)

                        # UOM
                        line_elements = _find_value('.//inv:unitName', element)
                        if line_elements:
                            invoice_line_form.product_uom_id = self._retrieve_uom(line_elements)

                        # Price Unit
                        line_elements = _find_value('.//inv:unitPrice', element)
                        invoice_line_form.price_unit = line_elements and float(line_elements) or 0.0

                        # Taxes
                        tax_element = _find_value('.//inv:vatPercentage', element)
                        invoice_line_form.tax_ids.clear()
                        tax = self_ctx._retrieve_tax(
                            amount=tax_element,
                            type_tax_use=invoice_form.journal_id.type
                        )
                        if tax:
                            invoice_line_form.tax_ids.add(tax)
        invoice = invoice_form.save()
        return invoice
