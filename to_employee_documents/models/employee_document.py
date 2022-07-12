from odoo import models, fields, api, _
from datetime import timedelta
from odoo.exceptions import UserError, ValidationError


class EmployeeDocument(models.Model):
    _name = 'employee.document'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Employee Document"

    name = fields.Char(string='Doc. Number', required=True, tracking=True)

    kept_by = fields.Selection([
        ('employee', 'Employee'),
        ('company', 'The Company')], required=True, default='employee', string='Being kept by', tracking=True,
        help="Whom this document is being kept by."
    )
    user_id = fields.Many2one('res.users', string='Document Manager', required=True, default=lambda self: self.env.user,
                              tracking=True, help="The employee in your"
                                                " HR Department that takes responsibility for managing this document")
    type_id = fields.Many2one('employee.document.type', string="Document Type", required=True, ondelete='restrict')
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, ondelete='cascade', tracking=True)
    company_id = fields.Many2one(related='employee_id.company_id', store=True)
    department_id = fields.Many2one('hr.department', related='employee_id.department_id', store=True)
    issue_date = fields.Date(string="Issue Date", tracking=True, help="The date on which this document was issued")
    expire_date = fields.Date(string='Expiration Date', tracking=True, help="The date on which this document gets expired")
    days_to_notify = fields.Integer(string='Days to Notify', default=0, tracking=True, required=True,
                                    help="The number of days priors to the expiration date "
                                        "to notify the employee and the document manager"
                                        " about the expiration. Leave it as zero (0) to disable the notification.")
    date_to_notify = fields.Date(string='Date to notify', compute='_compute_date_to_notify', store=True, tracking=True,
                                 help="Technical field that indicates the date on which the notification should be sent.")
    issued_by = fields.Many2one('res.partner', string='Issued By', tracking=True)
    place_of_issue = fields.Char(string="Place of Issue", tracking=True)
    notes = fields.Text(string='Notes')
    pdf = fields.Binary(string='PDF', help="Store the PDF version of the Document")
    image1 = fields.Binary(string='Image 1')
    image2 = fields.Binary(string='Image 2')
    return_upon_termination = fields.Boolean(string='Return Upon Termination', tracking=True,
                                             help="If checked, the original document must be return to its owner."
                                             " I.e. if the origin is kept by the company, it should be returned to the employee;")

    has_scanned_doc = fields.Boolean('Has Scanned Document attached', compute='_compute_has_scanned_doc', store=True)

    _sql_constraints = [
        ('emplyee_doc_type_doc_name_uniq',
         'unique(name, type_id, employee_id)',
         "The document number must be unique per document type per employee!"),
    ]

    def name_get(self):
        name = []
        for r in self:
            name.append((r.id, '%s / %s' % (r.type_id.name, r.employee_id.name)))
        return name

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('type_id.name', '=ilike', '%' + name + '%'), ('name', operator, name)]
        docs = self.search(domain + args, limit=limit)
        return docs.name_get()

    @api.constrains('issue_date','expire_date')
    def _check_issue_date_and_expire_date(self):
        #Check and compare between issue date and expire date
        for r in self:
            if r.expire_date and r.issue_date and r.expire_date < r.issue_date:
                raise ValidationError(_("Issue date must be before Expire date"))

    @api.constrains('kept_by', 'return_upon_termination')
    def _check_owner_cannot_return_to_himself(self):
        for r in self:
            if r.kept_by == 'employee' and r.return_upon_termination:
                raise UserError(_("Invalid action! This document %s cannot be returned to the owner "
                                "while it is already being kept by the owner.") % (r.name))

    @api.onchange('kept_by')
    def _onchange_kept_by(self):
        if self.kept_by == 'employee':
            self.return_upon_termination = False

    @api.onchange('issued_by')
    def _onchange_issued_by(self):
        issue_loc = []
        if self.issued_by:
            if self.issued_by.city:
                issue_loc.append(self.issued_by.city)
            if self.issued_by.state_id:
                issue_loc.append(self.issued_by.state_id.name)
            if self.issued_by.country_id:
                issue_loc.append(self.issued_by.country_id.name)
        if issue_loc:
            self.place_of_issue = ', '.join(issue_loc)

    @api.onchange('type_id')
    def _onchage_type_id(self):
        if self.type_id:
            if self.type_id.days_to_notify > 0:
                self.days_to_notify = self.type_id.days_to_notify
            self.kept_by = self.type_id.kept_by
            self.return_upon_termination = self.type_id.return_upon_termination

    @api.depends('pdf', 'image1', 'image2')
    def _compute_has_scanned_doc(self):
        for r in self:
            r.has_scanned_doc = True if r.pdf or r.image1 or r.image2 else False

    @api.depends('expire_date', 'days_to_notify')
    def _compute_date_to_notify(self):
        for r in self:
            if r.expire_date and r.days_to_notify > 0:
                r.date_to_notify = r.expire_date - timedelta(days=r.days_to_notify)
            else:
                r.date_to_notify = False

    def cron_notify_expire_docs(self):
        today = fields.Date.today()
        to_notify_docs = self.search([('date_to_notify', '<=', today)])
        to_notify_docs.action_send_expiry_notification()

    def action_send_expiry_notification(self):
        for r in self:
            email_template_id = self.env.ref('to_employee_documents.email_template_doc_expire_notif')
            r.message_post_with_template(email_template_id.id)

    def action_return_to_owner(self):
        for r in self:
            if r.kept_by != 'company':
                raise UserError(_("Invalid action. The document %s is already being kept by the employee") % (r.name,))
            elif not r.return_upon_termination:
                raise UserError(_("The document %s cannot be set to be kept by Employee "
                                  "as there is no need return back to the employee") % (r.name,))

        return self.write({'kept_by': 'employee', 'return_upon_termination': False})
