import base64

from odoo import api, models, fields, _
from odoo.modules.module import get_module_resource


class ResCompany(models.Model):
    _inherit = 'res.company'

    einvoice_service_id = fields.Many2one('einvoice.service', domain="[('provider', '!=', 'none')]", string='E-Invoice Service', copy=False)
    einvoice_lock_legal_number = fields.Boolean(string='Lock Legal Number', default=True,
                                              help="If checked, invoice's legal number will be locked after E-Invoice will be issued.")
    einvoice_issue_earliest_invoice_first = fields.Boolean(string='Issue Earlier Invoice First', default=True,
                                                         help="If checked, during issuing a new E-Invoice, Odoo will check to validate if there is an"
                                                         " existing invoice the invoice date of which is earlier than the current one's. If there is,"
                                                         " Odoo will stop you from issuing E-Invoice for the current one and ask you to do for the"
                                                         " earlier one priorily.")
    einvoice_exchange_file_as_attachment = fields.Boolean(string='Attach Invoice Converted Version', default=False,
                                                          help="If checked, when generating the converted version of the E-Invoice,"
                                                          " Odoo will also generate a corresponding attachment and attach it to the invoice.")
    einvoice_representation_file_as_attachment = fields.Boolean(string='Attach Invoice Repensentation Version', default=False,
                                                                help="If checked, when generating the representation version of the E-Invoice,"
                                                                " Odoo will also generate a corresponding attachment and attach it to the invoice.")
    einvoice_auto_issue = fields.Boolean(string='Auto Issue', copy=False, help="If checked, the system automatically issue e-invoices.")


    def _prepare_einvoice_service_data(self):
        self.ensure_one()
        sinvoice_image_path = get_module_resource('viin_l10n_vn_accounting_sinvoice', 'static/description', 'icon.png')
        vninvoice_image_path = get_module_resource('viin_l10n_vn_accounting_vninvoice', 'static/description', 'icon.png')
        return [
            {
                'name': _('S-Invoice API v1'),
                'image_128': base64.b64encode(open(sinvoice_image_path, 'rb').read()),
                'module_id': self.env.ref('base.module_viin_l10n_vn_accounting_sinvoice').id,
                'api_version': 'v1',
                'company_id': self.id,
                'description': _("Integrates with Viettel's S-Invoice service to issue legal E-Invoice. This service uses API version 1, which supporting both Circulars No.32/2011/TT-BTC and Circulars No.78/2021/TT-BTC."),
            },
            {
                'name': _('S-Invoice API v2'),
                'image_128': base64.b64encode(open(sinvoice_image_path, 'rb').read()),
                'module_id': self.env.ref('base.module_viin_l10n_vn_accounting_sinvoice').id,
                'api_version': 'v2',
                'company_id': self.id,
                'description': _("Integrates with Viettel's S-Invoice service to issue legal E-Invoice. This service uses API version 2, which supporting both Circulars No.32/2011/TT-BTC and Circulars No.78/2021/TT-BTC. This version has been added some more security features than version 1."),
            },
            {
                'name': _('VN-Invoice API v1'),
                'image_128': base64.b64encode(open(vninvoice_image_path, 'rb').read()),
                'module_id': self.env.ref('base.module_viin_l10n_vn_accounting_vninvoice').id,
                'api_version': 'v1',
                'company_id': self.id,
                'description': _("Integrates with VNPT's VN-Invoice service to issue legal E-Invoice. This service uses API version 1, which supporting Circulars No.32/2011/TT-BTC."),
            },
            {
                'name': _('VN-Invoice API v2'),
                'image_128': base64.b64encode(open(vninvoice_image_path, 'rb').read()),
                'module_id': self.env.ref('base.module_viin_l10n_vn_accounting_vninvoice').id,
                'api_version': 'v2',
                'company_id': self.id,
                'description': _("Integrates with VNPT's VN-Invoice service to issue legal E-Invoice. This service uses API version 2, which supporting Circulars No.78/2021/TT-BTC."),
            },
        ]

    @api.model_create_multi
    @api.returns('self', lambda value:value.id)
    def create(self, vals_list):
        res = super(ResCompany, self).create(vals_list)
        res._create_einvoice_services_vn_company()
        return res

    def _create_einvoice_services_vn_company(self):
        """Create einvoice.service for VN company"""
        vn_country = self.env.ref('base.vn')
        EinvoiceService = self.env['einvoice.service'].sudo()
        vals_list = []
        for r in self:
            if r.country_id != vn_country:
                continue
            vals_list.extend(r._prepare_einvoice_service_data())
        if vals_list:
            EinvoiceService.create(vals_list)
