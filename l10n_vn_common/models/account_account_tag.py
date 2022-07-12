from odoo import models, fields, api


class AccountAccountTag(models.Model):
    _inherit = 'account.account.tag'

    code = fields.Char(string='Code', size=20, help="The unique code of the tag")

    def name_get(self):
        result = []
        for r in self:
            if r.code:
                result.append((r.id, '%s - %s' % (r.code, r.name)))
            else:
                result.append((r.id, r.name))
        return result

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('code', '=ilike', name + '%'), ('name', operator, name)]
        tags = self.search(domain + args, limit=limit)
        return tags.name_get()
