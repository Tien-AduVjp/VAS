from odoo import fields, models, api
from odoo.addons.http_routing.models.ir_http import slug


class WebsiteDocTag(models.Model):
    _name = 'website.doc.tag'
    _description = 'Document Tag'
    _inherit = ['abstract.website.doc', 'website.seo.metadata']
    _order = 'name'

    document_ids = fields.Many2many('website.document', 'website_doc_tag_website_document_rel', 'tag_id', 'document_id', string='Website Documents',
                                  help="The documents that refer these tags")
    doc_category_ids = fields.Many2many('website.doc.category', 'website_doc_tag_website_doc_category_rel', 'tag_id', 'category_id', string='Website Document Categories')

    name = fields.Char('Name', required=True, index=True, translate=True)
    website_url = fields.Char('Website Url', compute='_compute_website_url')
    document_count = fields.Integer('Documents Count', compute='_get_document_count')

    _sql_constraints = [
        ('name', 'unique(name)', 'Tag name is exists!'),
    ]

    def _compute_website_url(self):
        for my in self:
            my.website_url = '/docs/t/%s' % slug(my)

    def _get_document_count(self):
        for r in self:
            r.document_count = len(r.document_ids)

