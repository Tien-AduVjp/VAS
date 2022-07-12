from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

from odoo.models import PREFETCH_MAX


class DocumentAutoGenerateRule(models.Model):
    _name = 'document.auto.generate.rule'
    _description = 'Document Attachment Setting'
    _rec_name = 'res_model_id'

    res_model_id = fields.Many2one('ir.model', string='Model', required=True, ondelete='cascade')
    res_model_name = fields.Char(related='res_model_id.model', string='Model Name')
    active = fields.Boolean(string='Active', default=True)
    workspace_field_id = fields.Many2one('ir.model.fields', string='Workspace Field',
        help="Field to create workspace. Ex. : With Project field of Project Task model. It will create document of task into Project workspace")
    parent_workspace_id = fields.Many2one('document.workspace', string='Parent Workspace')
    workspace_tag_ids = fields.Many2many('document.tag', string='Tags')
    workspace_action_ids = fields.Many2many('document.action', string='Actions')
    # workspace team access right
    workspace_write_team_ids = fields.Many2many('document.team', 'document_auto_generate_rule_workspace_write_team', string='Writable Teams',
        help="Teams can read, upload and edit its documents")
    workspace_read_team_ids = fields.Many2many('document.team', 'document_auto_generate_rule_workspace_read_team', string='Readable Teams',
        help="Teams can read only its documents")
    workspace_specific_team_ids = fields.Many2many('document.team', 'document_auto_generate_rule_workspace_specific_team', string='Teams Own Document Only',
        help="All members of teams can read, upload and edit its documents of which they are owner")

    # workspace user access right
    workspace_write_user_ids = fields.Many2many('res.users', 'document_auto_generate_rule_workspace_write_user', string='Writable Users',
        help="Users can read, upload and edit its documents")
    workspace_read_user_ids = fields.Many2many('res.users', 'document_auto_generate_rule_workspace_read_user', string='Readable users',
        help="Users can read only its documents")
    workspace_specific_user_ids = fields.Many2many('res.users', 'document_auto_generate_rule_workspace_specific_user', string='Users Own Document Only',
        help="Users can read, upload and edit its documents of which they are owner")

    # group access right
    workspace_write_group_ids = fields.Many2many('res.groups', 'document_auto_generate_rule_workspace_write_group', string='Writable Groups',
        help="User groups can read, upload and edit its documents")
    workspace_read_group_ids = fields.Many2many('res.groups', 'document_auto_generate_rule_workspace_read_group', string='Readable Groups',
        help="User groups can read only its documents")
    workspace_specific_group_ids = fields.Many2many('res.groups', 'document_auto_generate_rule_workspace_specific_group', string='Groups Own Document Only',
        help="User groups can read, upload and edit its documents of which they are owner")

    _sql_constraints = [
        ('res_model_id', 'unique (res_model_id)', 'The resource model must be unique!')
    ]

    @api.constrains('res_model_id', 'workspace_field_id')
    def _check_workspace_field(self):
        for r in self:
            if r.workspace_field_id:
                if r.workspace_field_id.model_id != r.res_model_id:
                    raise ValidationError(_("Cannot create document auto generate rule for model because Workspace Field '%s'\
                                            does not belong to model '%s'") % (r.workspace_field_id.name, r.res_model_id.model))
                if r.workspace_field_id.ttype not in ('many2one', 'selection', 'date', 'datetime', 'char'):
                    raise ValidationError(_("Workspace Field '%s' has type not supported.\n\
                                            Please select 'many2one', 'selection', 'date, or 'datetime' field") % r.workspace_field_id.name)

    def run_manual(self):

        def splittor(rs):
            """ Splits the found attachment recordset in batches of 1000 (to avoid
            entire-recordset-prefetch-effects) & removes the previous batch
            from the cache after it's been iterated in full
            @return: return an iterator
            """
            for idx in range(0, len(rs), PREFETCH_MAX):
                sub = rs[idx:idx + PREFETCH_MAX]
                yield sub
                rs.invalidate_cache(ids=sub.ids)

        non_doc_attachments = self.env['ir.attachment'].search([
            ('document_ids', '=', False),
            ('res_model', 'in', self.mapped('res_model_id.model'))
            ])
        if not non_doc_attachments:
            return
        # read for pre-fetching benefit
        non_doc_attachments.read(['res_model'])

        for r in self:
            to_process = non_doc_attachments.filtered(lambda a: a.res_model == r.res_model_id.model)
            for attachments in splittor(to_process):
                attachments.with_context(tracking_disable=True)._generate_document(r)
        # rewrite magic fields
        if non_doc_attachments.ids:
            self.env.cr.execute("""
            UPDATE document_document d
            SET create_date = att.create_date,
                write_date = att.write_date,
                create_uid = att.create_uid,
                write_uid = att.write_uid
            FROM ir_attachment att
            WHERE d.attachment_id = att.id AND att.id in %s
            """, (tuple(non_doc_attachments.ids),))
