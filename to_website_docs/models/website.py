from odoo import models
import json


class Website(models.Model):
    _inherit = 'website'

    def _prepare_docs_domain(self):
        domain = [
            '|', ('lang_ids.code', 'in', [self._context.get('lang', 'en_US')]), ('lang_ids', '=', False),
            '|', ('website_id', '=', self.id), ('website_id', '=', False)]

        # If the document is not published and the user is neither the creator nor the author nor the author's staff
        user = self.env.user
        if not user.has_group('to_website_docs.group_website_doc_editor'):
            domain += [
                '|', ('website_published', '=', True),
                    '&', ('website_published', '=', False),
                        '|', ('create_uid', '=', user.id), ('author_id', '=', user.partner_id.commercial_partner_id.id)]
        return domain

    def _prepare_docs_categ_domain(self):
        domain = [
            '|', ('lang_ids.code', 'in', [self._context.get('lang', 'en_US')]), ('lang_ids', '=', False),
            '|', ('website_id', '=', self.id), ('website_id', '=', False)]
        user = self.env.user
        if not user.has_group('to_website_docs.group_website_doc_editor'):
            domain = ['&', '|', ('website_published', '=', True), ('create_uid', '=', user.id)] + domain
        return domain

    def _get_docs_subjects_domain(self):
        domain = [('parent_id', '=', False)] + self._prepare_docs_categ_domain()
        return domain

    def get_docs_subjects(self):
        return self.env['website.doc.category'].search(self._get_docs_subjects_domain())

    def get_role_category(self):
        role_create = False
        role_write = False
        role_unlink = False
        if self.env.user.has_group('to_website_docs.group_website_doc_manager'):
            role_create = role_write = role_unlink = True
        elif self.env.user.has_group('to_website_docs.group_website_doc_reviewer'):
            role_create = role_write = True
        return json.dumps({'role_create': role_create,
                'role_write': role_write,
                'role_unlink': role_unlink
                })