from odoo import models, fields, _
from odoo.exceptions import UserError


class AccountEInvoiceType(models.Model):
    _name = 'account.einvoice.type'
    _description = 'E-Invoice Type'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Code', required=True, tracking=True,
                       help="The E-Invoice type's code that provided by provider.")
    invoice_ids = fields.One2many('account.move', 'account_einvoice_type_id', string='Invoices', readonly=True, copy=False,
                                  help="The invoices associated with this invoice type")
    description = fields.Char(string='Description', translate=True)

    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         "The code must be unique!"),
    ]

    def write(self, vals):
        if 'name' in vals:
            for r in self:
                if r.invoice_ids:
                    raise UserError(_("You cannot modify the Code of the invoice type %s to %s while it is referred by the invoice %s."
                                      " You should either delete all the related invoices or create another invoice type.")
                                    % (r.name, vals['name'], r.invoice_ids[0].name or r.invoice_ids[0].legal_number))
        return super(AccountEInvoiceType, self).write(vals)

