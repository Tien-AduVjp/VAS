from odoo import fields, models


class DocumentPublicRule(models.Model):
    _name = 'docs.public.rule'
    _description = 'Document Public Rule'

    sequence = fields.Integer('Sequence', default=10)
    category_id = fields.Many2one('website.doc.category', 'Category', index=True)
    groups_id = fields.Many2many('res.groups', 'res_groups_docs_public_rule_rel', 'doc_public_rule_id', 'res_group_id', string='Groups', domain=[('share','=',False)])
    users = fields.Many2many('res.users', 'res_users_docs_public_rule_rel', 'doc_public_rule_id', 'user_id', string='Users')
    public_type = fields.Selection([
        ('100', '100%'),
        ('50', '50%'),
        ('25', '25%'),
        ('0', 'None')], string='Public Type', index=True)
