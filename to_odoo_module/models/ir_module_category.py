from odoo import models, fields


class IrModuleCategory(models.Model):
    _inherit = 'ir.module.category'

    parent_id = fields.Many2one(auto_join=True)

    def guess_category_from_string(self, category_name_str):
        """
        @param category_name_str: string in form of something like 'Parent Category/Category'
            or 'Parent of Parent Category/Parent Category/Category' with nested categories support
        """

        def get_categ(domain):
            """
            @param domain: something like [('name', '=', 'Category'), ('parent_id.name', '=', 'Parent Category'), ('parent_id.parent_id.name', '=', 'Parent of Parent Category')]
            @return: ir.module.category record
            """
            category = self.env['ir.module.category'].sudo().search(domain, limit=1)
            if category:
                return category
            else:
                domain = domain[:-1]
                if not domain:
                    uncategorized = self.env['ir.module.category'].sudo().search([('name', '=', 'Uncategorized')], limit=1)
                    return uncategorized
                return get_categ(domain)

        domain = []
        # building domain which could result something like
        # [
        #    ('name', '=', 'Category'),
        #    ('parent_id.name', '=', 'Parent Category'),
        #    ('parent_id.parent_id.name', '=', 'Parent of Parent Category')
        #    ]
        for i, categ in enumerate(reversed(category_name_str.split('/'))):
            categ = categ.strip()
            if i == 0:
                domain.append(('name', '=', categ))
            else:
                # create a list of i elements of 'parent_id'
                fields_list = ['parent_id'] * i
                # build domain field
                field = '%s.name' % '.'.join(fields_list)
                # append tuple condition into the domain
                domain.append((field, '=', categ))

        return get_categ(domain)
