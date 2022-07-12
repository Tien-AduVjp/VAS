from odoo import models, fields


class WebsiteDocCategory(models.Model):
    _inherit = 'website.document'

    path_in_branch = fields.Char(string='Path in Branch', index=True,
                                 help="Technical field to store the relative path of the corresponding HTML file in the branch"
                                 " - the file the content of which is loaded in to this contents' fulltext of this document.")

    def _get_merge_fields_data(self):
        data = super(WebsiteDocCategory, self)._get_merge_fields_data()
        if self.path_in_branch:
            data['path_in_branch'] = self.path_in_branch
        return data

