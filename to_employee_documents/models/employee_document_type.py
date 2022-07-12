from odoo import models, fields, api, _
from odoo.exceptions import UserError

class EmployeeDocumentType(models.Model):
    _name = 'employee.document.type'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Employee Document Type"

    name = fields.Char(string='Name', required=True, translate=True)
    type = fields.Selection([
        ('national_id', 'National ID'),
        ('passport', 'Passport'),
        ('hr_contract', 'Labor Contract'),
        ('social', 'Social Related Docs'),
        ('others', 'Others')], required=True, index=True, string='Type')
    description = fields.Text(string='Description')
    days_to_notify = fields.Integer(string='Days to Notify', default=7, tracking=True, required=True,
                                    help="The default number of days for documents of this type to raise a notification"
                                        " before they get expired")
    kept_by = fields.Selection([
        ('employee', 'Employee'),
        ('company', 'The Company')], required=True, default='employee', string='Being kept by',
         help="Whom this document is being kept by."
    )
    return_upon_termination = fields.Boolean(string='Return Upon Termination', tracking=True,
                                             help="The default value for the documents of this type to indicate if the"
                                                " origin of the document should be returned to its owner upon termination")

    @api.onchange('kept_by')
    def _onchange_kept_by(self):
        if self.kept_by == 'employee':
            self.return_upon_termination = False


    @api.constrains('kept_by', 'return_upon_termination')
    def _check_owner_cannot_return_to_himself(self):
        for r in self:
            if r.kept_by == 'employee' and r.return_upon_termination:
                raise UserError(_("Invalid configuration! This type of document cannot be set returned to the owner "
                                "while it is already being kept by the owner."))
