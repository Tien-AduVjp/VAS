from odoo import api, SUPERUSER_ID


def _generate_config_params(env):
    env['res.company']._generate_sinvoice_config_params()


def _migrate_sinvoice_state(env):
    issued_invoices = env['account.invoice'].search([('electric_invoice_created', '=', True)])
    if issued_invoices:
        issued_invoices.write({
            'sinvoice_state': 'issued'
            })


def _generate_sinvoice_type_from_deprecated_sinvoice_api_invoice_type_if_not_exists(env):
    SInvoiceType = env['account.sinvoice.type']
    for company in env['res.company'].search([]):
        sinvoice_api_invoice_type = company.sinvoice_api_invoice_type
        if sinvoice_api_invoice_type:
            sinvoice_type_id = SInvoiceType.search([('name', '=', sinvoice_api_invoice_type)], limit=1)
            if not sinvoice_type_id:
                sinvoice_type_id = SInvoiceType.create({
                    'name': sinvoice_api_invoice_type,
                    })
        else:
            sinvoice_type_id = SInvoiceType.search([('name', '=', '01GTKT')], limit=1)
        company.write({
            'account_sinvoice_type_id': sinvoice_type_id.id
            })


def _generate_sinvoice_template_from_deprecated_sinvoice_api_invoice_template_if_not_exists(env):
    SInvoiceTemplate = env['account.sinvoice.template']
    for company in env['res.company'].search([]):
        data = {}
        sinvoice_api_invoice_template = company.sinvoice_api_invoice_template
        if sinvoice_api_invoice_template:
            sinvoice_template_id = SInvoiceTemplate.search([('name', '=', sinvoice_api_invoice_template)], limit=1)
            if not sinvoice_template_id:
                sinvoice_template_id = SInvoiceTemplate.create({
                    'name': sinvoice_api_invoice_template,
                    'type_id': company.account_sinvoice_type_id.id
                    })
            data.update({
                'account_sinvoice_template_id': sinvoice_template_id.id,
                'sinvoice_mode': 'production',
                })
        else:
            sinvoice_template_id = SInvoiceTemplate.search([('name', '=', '01GTKT0/001')], limit=1)
            data.update({
                'account_sinvoice_template_id': sinvoice_template_id.id
                })
        if bool(data):
            company.write(data)


def _generate_sonthanh_serials(env):
    Serial = env['account.sinvoice.serial']
    sinvoice_template_01GTKT0_001 = env.ref('to_accounting_sinvoice.sinvoice_template_01GTKT0_001')
    for company in env['res.company'].search([]):
        vat = company.vat
        data = {
            'template_id': sinvoice_template_01GTKT0_001.id
            }
        # Công ty An Hải Thành
        if vat == '0313525277':
            data.update({
                'name': 'HT/18E',
                })
        # Công ty Hoàng Tấn Phát
        elif vat == '0309588732':
            data.update({
                'name': 'HT/18E',
                })
        # Công ty Sơn Thanh
        elif vat == '0314540084':
            data.update({
                'name': 'ST/18E',
                })
        if 'name' in data:
            serial = env['account.sinvoice.serial'].create(data)
            company.write({
                'account_sinvoice_serial_id': serial.id
                })
            issued_invoices = env['account.invoice'].search([('sinvoice_state', '!=', 'not_issued'), ('company_id', '=', company.id)])
            if issued_invoices:
                issued_invoices.write({
                    'account_sinvoice_serial_id': company.account_sinvoice_serial_id.id,
                    'account_sinvoice_template_id': company.account_sinvoice_template_id.id,
                    'account_sinvoice_type_id': company.account_sinvoice_type_id.id,
                    })


def _ensure_sinvoice_files(env):
    issued_invoices = env['account.invoice'].search([('sinvoice_state', '!=', 'not_issued')])
    for invoice in issued_invoices:
        invoice._ensure_sinvoice_representation_files()
        invoice._ensure_sinvoice_converted_file()


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _generate_config_params(env)
    _migrate_sinvoice_state(env)
    _generate_sinvoice_type_from_deprecated_sinvoice_api_invoice_type_if_not_exists(env)
    _generate_sinvoice_template_from_deprecated_sinvoice_api_invoice_template_if_not_exists(env)

    # TODO: remove after upgrade for Son Thanh
    _generate_sonthanh_serials(env)

    _ensure_sinvoice_files(env)

