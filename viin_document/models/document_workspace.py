from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class DocumentWorkspace(models.Model):
    _name = 'document.workspace'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _parent_name = "parent_id"
    _parent_store = True
    _rec_name = 'complete_name'
    _description = "Document Workspace"

    name = fields.Char(string='Name', required=True, tracking=True)
    complete_name = fields.Char(string='Complete Name', compute='_compute_complete_name', store=True)
    parent_id = fields.Many2one('document.workspace', 'Parent Workspace', index=True, ondelete='cascade', tracking=True)
    parent_path = fields.Char(string='Parent Path', index=True)
    child_ids = fields.One2many('document.workspace', 'parent_id', 'Child Workspaces')
    recursive_child_ids = fields.Many2many('document.workspace', 'recursive_document_workspace', 'parent_id', 'child_id',
                                           string='Recursive Child Workspaces', compute='_compute_recursive_child_ids', store=True)
    action_ids = fields.Many2many('document.action', string='Actions')
    tag_ids = fields.Many2many('document.tag', string='Tags')
    company_id = fields.Many2one('res.company', 'Company', groups="base.group_multi_company", help="For multi company", tracking=True,
        default=lambda self: self.env.company)
    description = fields.Text(string='Description', help="Can be used to show tooltip on some views")
    unique_doc_name = fields.Boolean(string='Document Unique Name',
                                    help="If enabled, a new document uploaded into this workspace will be checked if "
                                        "its name violates unique rule. In other words, documents in this workspace must have different names",
                                    default=lambda self: self.env.company.unique_doc_name)
    active = fields.Boolean(string='Active', default=True)

    # team access right
    write_team_ids = fields.Many2many('document.team', 'document_workspace_write_team', string='Writable Teams',
        help="Teams can read, upload and edit its documents")
    read_team_ids = fields.Many2many('document.team', 'document_workspace_read_team', string='Readable Teams',
        help="Teams can read only its documents")
    specific_team_ids = fields.Many2many('document.team', 'document_workspace_specific_team', string='Teams Own Document Only',
        help="All members of teams can read, upload and edit its documents of which they are owner")

    # user access right
    write_user_ids = fields.Many2many('res.users', 'document_workspace_write_user', string='Writable Users',
        help="Users can read, upload and edit its documents")
    read_user_ids = fields.Many2many('res.users', 'document_workspace_read_user', string='Readable users',
        help="Users can read only its documents")
    specific_user_ids = fields.Many2many('res.users', 'document_workspace_specific_user', string='Users Own Document Only',
        help="Users can read, upload and edit its documents of which they are owner")

    # group access right
    write_group_ids = fields.Many2many('res.groups', 'document_workspace_write_group', string='Writable Groups',
        help="User groups can read, upload and edit its documents")
    read_group_ids = fields.Many2many('res.groups', 'document_workspace_read_group', string='Readable Groups',
        help="User groups can read only its documents")
    specific_group_ids = fields.Many2many('res.groups', 'document_workspace_specific_group', string='Groups Own Document Only',
        help="User groups can read, upload and edit its documents of which they are owner")
    document_ids = fields.One2many('document.document', 'workspace_id', string='Documents')

    def name_get(self):
        if not self.env.context.get('hierarchical_naming', True):
            return [(record.id, record.name) for record in self]
        return super(DocumentWorkspace, self).name_get()

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for r in self:
            if r.parent_id:
                r.complete_name = '%s / %s' % (r.parent_id.complete_name, r.name)
            else:
                r.complete_name = r.name

    def _get_nested_children(self):
        child_ids = self.mapped('child_ids')
        for child_id in child_ids:
            child_ids += child_id._get_nested_children()
        return child_ids

    @api.depends('child_ids', 'child_ids.recursive_child_ids')
    def _compute_recursive_child_ids(self):
        for r in self:
            r.recursive_child_ids = r._get_nested_children()

    @api.constrains('parent_id')
    def _check_workspace_recursion(self):
        if not self._check_recursion():
            raise ValidationError(_('You cannot create recursive workspaces.'))
        return True

    @api.model
    def name_create(self, name):
        return self.create({'name': name}).name_get()[0]

    def action_view_documents(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('viin_document.document_document_action')
        action['context'] = {
            'searchpanel_default_workspace_id': self.id,
            }
        return action
