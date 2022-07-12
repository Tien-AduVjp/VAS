from odoo import models, fields


class GitBranch(models.Model):
    _inherit = 'git.branch'

    website_doc_category_id = fields.Many2one('website.doc.category', help="The website document category for which this branch serves")
    documents_discovered_once = fields.Boolean('website.doc.category', help="Technical field is to indicate if this branch was once fetched for documents")
