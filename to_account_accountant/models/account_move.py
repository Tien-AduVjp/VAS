from odoo import fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    manual_entry = fields.Boolean(string='Manual Direct Entry', readonly=True, copy=False,
                                  help="Accountants are not encouraged to encode accounting with direct and manual entries"
                                  " (from the menu Accounting > Accounting > Miscellaneous > Journal Entries). When they do"
                                  " so, we need to know that by checking this field automatically.")

    attachment_ids = fields.One2many('ir.attachment', 'res_id', domain=[('res_model', '=', 'account.move')], string='Attachments')
    post_date = fields.Datetime(string='Posted Date', readonly=True, tracking=True, copy=False,
                                help="The date and time at which the entry was posted.")
    invoice_date = fields.Date(tracking=True)

    def _post(self, soft=True):
        res = super(AccountMove, self)._post(soft)
        self.write({'post_date': fields.Datetime.now()})
        return res
