from odoo import models, fields, _
from odoo.exceptions import UserError


class AccountEInvoiceTemplate(models.Model):
    _name = 'account.einvoice.template'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Account E-Invoice Type'

    name = fields.Char(string='Name', required=True, tracking=True,
                       help="The name of the invoice template that provided by provider.")
    type_id = fields.Many2one('account.einvoice.type', string='E-Invoice Type', tracking=True, required=True)
    invoice_ids = fields.One2many('account.move', 'account_einvoice_template_id', string='Invoices', readonly=True, copy=False,
                                  help="The invoices associated with this E-Invoice template")
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
        return super(AccountEInvoiceTemplate, self).write(vals)
