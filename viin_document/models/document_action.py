from odoo import fields, models

class DocumentAction(models.Model):
    _name = 'document.action'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Document Action"

    name = fields.Char(string='Name', required=True, translate=True)

    # Condition fields to run a action
    condition_type = fields.Selection([
        ('standard', 'Standard'),
        ('domain', 'Domain')
    ], string='Condition Type', default='standard', required=True,
        help="Condition to run this action. Keep empty to ignore condition\n"
            "Standard condition: this action will be run if some conditions are matched, ex. match included/exclued tags, owner.\n"
            "Domain condition: this action will be run if a domain is matched.\n")
    included_tag_ids = fields.Many2many('document.tag', 'document_action_included_tag_rel', 'document_id', 'tag_id',
        string='Included Tags', help="This action run only if document include these tag")
    excluded_tag_ids = fields.Many2many('document.tag', 'document_action_excluded_tag_rel', 'document_id', 'tag_id',
        string='Excluded Tags', help="This action run only if document exclude these tag")
    owner_id = fields.Many2one('res.users', string='Owner',
        help="This action run only if document owned by this owner")
    domain = fields.Char(string='Filter Domain', help="This action run only if the domains are matched")

    # Actions
    set_owner_id = fields.Many2one('res.users', string='Set Owner', help="This action will be set the owner for a document after run.")
    move_to_workspace_id = fields.Many2one('document.workspace', string='Move to Workspace',
        help="This action will be move a document to the workspace after run.")
    create_model = fields.Selection([], string='Create', help="This action will be create a record of the model.")
    set_tag_ids = fields.One2many('document.action.set_tag', 'action_id', string='Set Tags', help="This action will be set tags for a document after run.")

    # Schedule Activity
    done_document_activity = fields.Boolean(string='Mark all activities as done',
        help="If checked, this action will be done all activities of a document as done")
    create_document_activity = fields.Boolean(string='Schedule Activity',
        help="If checked, this action will be schedule a activity")
    document_activity_type_id = fields.Many2one('mail.activity.type', string='Activity Type', help="This action will be set activity type during create it")
    document_activity_due_date = fields.Integer(string='Due Date in', help="Set due date for activity during create it")
    document_activity_due_date_type = fields.Selection([
        ('day', 'Days'),
        ('week', 'Week'),
        ('month', 'Month'),
    ], string='Activity Due Date Type', help="The due date of activity in day or week or month")
    document_activity_summary = fields.Char(string='Activity Summary', help="This action will be set activity summary during create it")
    document_activity_user_id = fields.Many2one('res.users', string='Activity Assigned To', help="This action will be set responsible of activity during create it")
    document_activity_note = fields.Text(string='Activity Note', help="This action will be set activity note during create it")
    show_create_model = fields.Boolean(string='Show Create Model', default=lambda self: True if len(self._fields['create_model'].selection) else False,
        help="Be default, create_model field is abstract, it created for other module inherit.\n"
            "So, we need invisible it if has not any module use it.\n"
            "This is a technical field to compute and show or disable 'create_model' field on views")
    description = fields.Text(string='Description', help="Can be used to show tooltip on some views")
    active = fields.Boolean(string='Active', default=True)
