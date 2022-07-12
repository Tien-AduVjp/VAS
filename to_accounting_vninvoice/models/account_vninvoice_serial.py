from odoo import models, fields, _
from odoo.exceptions import UserError


# -------------------------------------------------
# serial will be used for prefixing vninvoice number
# and must be registered with VN-invoice priorily
# -------------------------------------------------
class AccountVNinvoiceSerial(models.Model):
    _name = 'account.vninvoice.serial' # In version 14: Change _name to 'account.einvoice.serial' and move to 'to_einvoice_common' module
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'VN-invoice Serial'

    name = fields.Char(string='Serial', required=True, tracking=True,
                       help="The prefix (e.g. AA/16E, AA/17E, etc) of the invoice number that must be registered"
                       " with VN-invoice priorily. See the Circular No. 39/2014/TT-BTC dated March 31, 2014 by The Ministry of Finance of Vietnam.")
    expiration = fields.Datetime(string='Expiration', help="The date and time at which this serial becomes expired and will not be able to used")
    template_id = fields.Many2one('account.vninvoice.template', string='VN-invoice Template', required=True, tracking=True)
    type_id = fields.Many2one(related='template_id.type_id')
    description = fields.Char(string='Description', translate=True)
    invoice_ids = fields.One2many('account.move', 'account_vninvoice_serial_id', string='Invoices', readonly=True, copy=False,
                                  help="The invoices associated with this serial")

    def write(self, vals):
        if 'name' in vals:
            for r in self:
                if r.invoice_ids:
                    raise UserError(_("You cannot modify the Serial %s to %s while it is referred by the invoice %s."
                                      " You should either delete all the related invoices or create another serial.")
                                    % (r.name, vals['name'], r.invoice_ids[0].name or r.invoice_ids[0].legal_number))
        return super(AccountVNinvoiceSerial, self).write(vals)
