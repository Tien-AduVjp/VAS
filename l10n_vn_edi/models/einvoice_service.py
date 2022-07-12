from requests.auth import HTTPBasicAuth
from odoo import models, fields


class EinvoiceService(models.Model):
    _name = 'einvoice.service'
    _description = 'E-Invoice Services'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'module_state, provider, name'

    name = fields.Char(string='Name', required=True, translate=True)
    description = fields.Text(string='Description', translate=True)
    provider = fields.Selection([('none', 'None')], copy=False, required=True, default='none',
                                         string='Provider')
    mode = fields.Selection([
        ('sandbox', 'Sandbox'), ('production', 'Production')], default='sandbox', copy=False, required=True,
        string='Mode', help="Choose Sandbox mode for testing before switch it to Production")
    start_date = fields.Date(string='Start Date',
                             help="The date from which your company announced the start of using E-Invoice.")
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id, required=True)
    api_url = fields.Char(string='API URL', copy=False)
    sandbox_api_url = fields.Char(string='Sandbox API URL', copy=False)
    username = fields.Char('Username', copy=False)
    password = fields.Char('Password', copy=False)
    sandbox_username = fields.Char('Sandbox Username', copy=False)
    sandbox_password = fields.Char('Sandbox Password', copy=False)
    image_128 = fields.Image("Image", max_width=128, max_height=128)
    module_id = fields.Many2one('ir.module.module', string='Corresponding Module')
    module_state = fields.Selection(string='Installation State', related='module_id.state', store=True)
    api_version = fields.Selection([('v1', 'API v1'), ('v2', 'API v2')], string='API Version', default='v1',
                                            copy=False, required=True,
                                            help="Versions corresponding to laws of rule in VietNam:"
                                                 "\nWith Vietel S-Invoice Provider:"
                                                 "\n- V1 and V2 both support Circulars No.32/2011/TT-BTC and Circulars No.78/2021/TT-BTC"
                                                 "\nWith VNPT VN-Invoice Provider:"
                                                 "\n- V1 supports Circulars No.32/2011/TT-BTC"
                                                 "\n- V2 supports Circulars No.78/2021/TT-BTC"
                                                 "\nYou should check the version of your e-invoice services before choosing versions here")
    access_token = fields.Char(string='Access Token', copy=False)
    refresh_token = fields.Char(string='Refresh Token', copy=False)
    token_validity = fields.Datetime(string='Token Validity', copy=False)

    def get_einvoice_auth_str(self):
        self.ensure_one()
        username = self.username if self.mode == 'production' else self.sandbox_username
        password = self.password if self.mode == 'production' else self.sandbox_password
        return HTTPBasicAuth(username, password)

    def _get_einvoice_api_url(self):
        """
        Return S-Invoice API URL according to the S-Invoice Mode which is either sandbox or production
        """
        self.ensure_one()
        return self.api_url if self.mode == 'production' else self.sandbox_api_url

    def button_immediate_install(self):
        """
        Install the einvoice service 's module and reload the page.
        """
        self.ensure_one()
        if self.module_id and self.module_state != 'installed':
            self.module_id.button_immediate_install()
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }
