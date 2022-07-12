from odoo import models, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def name_get(self):
        result = []
        for r in self:
            barcode = r.sudo().barcode
            if barcode:
                result.append((r.id, '[%s] %s' % (barcode, r.name)))
            else:
                result.append((r.id, r.name))
        return result

    def _build_name_seach_domain(self, name, operator='ilike', limit=100):
        domain = []
        if name:
            domain = ['|', ('barcode', 'ilike', name), ('name', operator, name)]
        return domain

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = self._build_name_seach_domain(name, operator, limit)
        tags = self.search(domain + args, limit=limit)
        return tags.name_get()
