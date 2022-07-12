from odoo import fields, models, api
from odoo.addons.to_base.models.to_base import after_commit


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    document_ids = fields.One2many('document.document', 'attachment_id', string='Documents')

    @api.model_create_multi
    def create(self, vals_list):
        attachments = super(IrAttachment, self).create(vals_list)
        if not self._context.get('do_not_generate_document_on_create', False):
            attachments._generate_document_after_commit()
        return attachments

    def write(self, vals):
        res = super(IrAttachment, self).write(vals)
        if 'res_model' in vals and not self._context.get('do_not_generate_document_on_write', False):
            self._generate_document_after_commit()
        return res

    def unlink(self):
        # If current user delete his own uploaded attachment, we'll allow that
        # and the relating document will be deleted too. But if he's trying to
        # delete someone else's attachment, we'll have to check his permission
        # on the relating document first.
        for r in self:
            if not r.create_uid.id == self.env.uid and r.document_ids:
                r.document_ids.check_access_rule('unlink')
        return super(IrAttachment, self).unlink()

    @after_commit
    def _generate_document_after_commit(self):
        with self.env.cr.savepoint():
            result = self.sudo().exists()._generate_document()
        return result

    def _generate_document(self, rules=None):
        """
        Auto generate document during create attachment based on document rule.

        NOTES:
            1. Attachments having no res_model (e.g. static resources like SCSS) will be ignored
            2. Attachments having no res_id (inconsistent data?) will be ignored
        """
        to_generate = self.filtered(lambda att: att.res_model and att.res_id)
        if not to_generate:
            return self.env['document.document']

        document_rules = rules or self.env['document.auto.generate.rule'].search([])
        vals_list = []
        for r in to_generate:
            rule = document_rules.filtered(lambda l: l.res_model_id.model == r.res_model)
            if rule:
                workspace = r._generate_document_workspace(rule)
                if workspace:
                    vals_list.append(r._prepare_document_vals(workspace))
        return self.env['document.document'].create(vals_list)

    def _prepare_document_vals(self, workspace):
        """
        Hook method to prepare document vals
        """
        res = {
            'name': self.name,
            'workspace_id': workspace.id,
            'attachment_id': self.id,
            'owner_id': self.create_uid.id,
            'url': self.url,
            'type': self.type,
        }
        return res

    def _generate_document_workspace(self, rule):
        """
        Auto create workspace based on workspace field. If exists then return the workspace
        """
        self.ensure_one()

        workspace = self.env['document.workspace']
        name = ''

        if rule.workspace_field_id.ttype == 'many2one':
            _model_record = self.env[self.res_model].browse(self.res_id).__getitem__(rule.workspace_field_id.name)
            if _model_record:
                name = _model_record.display_name

        elif rule.workspace_field_id.ttype == 'date' or rule.workspace_field_id.ttype == 'datetime':
            _field_val = self.env[self.res_model].browse(self.res_id).__getitem__(rule.workspace_field_id.name)
            if _field_val:
                name = _field_val.strftime('%m_%d_%Y'),

        elif rule.workspace_field_id.ttype == 'selection':
            _field_val = self.env[self.res_model].browse(self.res_id).__getitem__(rule.workspace_field_id.name)
            if _field_val:
                name = dict(self.env[self.res_model].browse(self.res_id)._fields[rule.workspace_field_id.name].selection).get(_field_val)

        elif rule.workspace_field_id.ttype == 'char':
            name = self.env[self.res_model].browse(self.res_id).__getitem__(rule.workspace_field_id.name)

        complete_name = ''
        if name:
            if rule.parent_workspace_id:
                complete_name = '%s / %s' % (rule.parent_workspace_id.complete_name, name)
            else:
                complete_name = name
        else:
            name = rule.parent_workspace_id.complete_name if rule.parent_workspace_id else self.env[self.res_model].browse(self.res_id).display_name
            complete_name = name

        if name:
            workspace = self.env['document.workspace'].sudo().search([('complete_name', '=', complete_name)], limit=1)
            if not workspace:
                vals = self._prepare_document_workspace_vals(name, rule)
                workspace = self.env['document.workspace'].sudo().create(vals)
        return workspace

    def _prepare_document_workspace_vals(self, name, rule):
        """
        Hook method to prepare document workspace vals
        """
        res = {
            'name': name,
            'parent_id': rule.parent_workspace_id.id,
            'tag_ids': rule.workspace_tag_ids,
            'action_ids': rule.workspace_action_ids,
            'write_team_ids': rule.workspace_write_team_ids,
            'read_team_ids': rule.workspace_read_team_ids,
            'specific_team_ids': rule.workspace_specific_team_ids,
            'write_user_ids': rule.workspace_write_user_ids,
            'read_user_ids': rule.workspace_read_user_ids,
            'specific_user_ids': rule.workspace_specific_user_ids,
            'write_group_ids': rule.workspace_write_group_ids,
            'read_group_ids': rule.workspace_read_group_ids,
            'specific_group_ids': rule.workspace_specific_group_ids,
        }
        return res
