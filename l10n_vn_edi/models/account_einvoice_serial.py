from odoo import models, fields, api, _
from odoo.exceptions import UserError


# -------------------------------------------------
# serial will be used for prefixing einvoice number
# and must be registered with E-Invoice priority
# -------------------------------------------------
class AccountEInvoiceSerial(models.Model):
    _name = 'account.einvoice.serial'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'E-Invoice Serial'

    name = fields.Char(string='Serial', required=True, tracking=True,
                       help="The prefix (e.g. AA/16E, AA/17E, etc) of the invoice number that must be registered"
                       " with E-Invoice priority. See the Circular No. 39/2014/TT-BTC dated March 31, 2014 by The Ministry of Finance of Vietnam.")
    einvoice_service_id = fields.Many2one('einvoice.service', string='E-Invoice Service',
                                          domain="[('provider', '!=', 'none')]", required=True, copy=False)
    company_id = fields.Many2one(related='einvoice_service_id.company_id', store=True)
    template_id = fields.Many2one('account.einvoice.template', string='E-Invoice Template', tracking=True)
    type_id = fields.Many2one(related='template_id.type_id')
    expiration = fields.Datetime(string='Expiration', help="The date and time at which this serial becomes expired and will not be able to used")
    description = fields.Char(string='Description', translate=True)
    invoice_ids = fields.One2many('account.move', 'account_einvoice_serial_id', string='Invoices', readonly=True, copy=False,
                                  help="The invoices associated with this serial")
    invoice_count = fields.Integer(compute='_compute_invoice_count')
    deprecated = fields.Boolean(string='Deprecated', copy=False)

    @api.depends('invoice_ids')
    def _compute_invoice_count(self):
        for r in self:
            r.invoice_count = len(r.invoice_ids)

    def write(self, vals):
        if 'name' in vals:
            for r in self:
                if r.invoice_ids:
                    raise UserError(_("You cannot modify the Serial %s to %s while it is referred by the invoice %s."
                                      " You should either delete all the related invoices or create another serial.")
                                    % (r.name, vals['name'], r.invoice_ids[0].name or r.invoice_ids[0].legal_number))
        return super(AccountEInvoiceSerial, self).write(vals)
