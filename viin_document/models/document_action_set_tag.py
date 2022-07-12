from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

class DocumentActionSetTag(models.Model):
    _name = 'document.action.set_tag'
    _description = "Document Action Set Tag"

    action_id = fields.Many2one('document.action', string='Action', ondelete='cascade')
    action_type = fields.Selection([
        ('add', 'Add Tags'),
        ('replace', 'Replace Tags'),
        ('remove', 'Remove Tags'),
    ], string='Action Type', required=True, default='add',
        help="Type of action to set tags after run action\n"
            "Add Tags: Tags will be add to a document.\n"
            "Replace Tags: Tags of a document will be replaced.\n"
            "Remove Tags: Tags of a document will be remove.\n")
    category_id = fields.Many2one('document.tag.category', string="Category")
    tag_ids = fields.Many2many('document.tag', string='Tags', help="Tags will be add or replace or remove")

    @api.constrains('category_id', 'tag_ids')
    def _check_tag_category(self):
        for r in self:
            if r.action_id and r.category_id and r.category_id not in r.tag_ids.category_ids:
                raise ValidationError(_("Cannot set tags for action '%s' because category and tags does not match.") % r.action_id.name)
