from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _unlink_doc_rule_group(env)
    
def _unlink_doc_rule_group(env):
    doc = env.ref("to_website_docs.model_website_document").id
    doc_content = env.ref("to_website_docs.model_website_document_content").id
    doc_category = env.ref("to_website_docs.model_website_doc_category").id
    ids = (doc_category,doc,doc_content)
    rules = env['ir.rule'].sudo().search([('model_id', 'in', ids)])
    
    category_id = env.ref("to_website_docs.module_group_document_management").id
    groups = env['res.groups'].sudo().search([('category_id', '=', category_id)])

    rules.unlink()
    groups.unlink()