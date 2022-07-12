from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountSInvoiceTemplate(models.Model):
    _name = 'account.sinvoice.template' # In version 14: Change _name to 'account.einvoice.template' and move to 'to_einvoice_common' modul
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Viettel S-Invoice Type'

    name = fields.Char(string='Name', required=True, tracking=True,
                       help="The name of the invoice template that provided by Viettel S-Invoice.")
    type_id = fields.Many2one('account.sinvoice.type', string='S-Invoice Type', tracking=True, required=True)
    invoice_ids = fields.One2many('account.move', 'account_sinvoice_template_id', string='Invoices', readonly=True, copy=False,
                                  help="The invoices associated with this S-Invoice template")
    description = fields.Char(string='Description', translate=True)

    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         "The name of the template must be unique!"),
    ]

    def write(self, vals):
        if 'name' in vals:
            for r in self:
                if r.invoice_ids:
                    raise UserError(_("You cannot modify the Name of the template %s to %s while it is referred by the invoice %s."
                                      " You should either delete all the related invoices or create another template.")
                                    % (r.name, vals['name'], r.invoice_ids[0].name or r.invoice_ids[0].legal_number))
        return super(AccountSInvoiceTemplate, self).write(vals)
