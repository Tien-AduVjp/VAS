from odoo import models


class Website(models.Model):
    _inherit = 'website'

    def get_docs_subjects(self, version=False):
        if version:
            categories = self.env['website.doc.category'].search(self._get_docs_subjects_domain())
            for category in categories:
                if not category.with_context(odoo_version_str=version).search_document():
                    categories -= category
            return categories
        return super(Website, self).get_docs_subjects()

