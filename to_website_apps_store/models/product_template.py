from odoo import models, fields, api, _
from odoo.exceptions import AccessError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    website_description = fields.Html(compute='_compute_website_description', inverse='_inverse_website_description', store=True)

    @api.depends('odoo_module_id.odoo_module_version_id.description', 'odoo_module_id.odoo_module_version_id.index_html')
    def _compute_website_description(self):
        for r in self:
            r.website_description = r.odoo_module_id.odoo_module_version_id.description_html

    def _inverse_website_description(self):
        for r in self.sudo():
            r.odoo_module_id.odoo_module_version_id.update({
                'replace_product_website_description': False,
                'description_html': r.website_description
                })

    def website_publish_button(self):
        if self._context.get('force', False):
            self.ensure_one()
            if self.env.user.has_group('website.group_website_publisher') or self.env.su:
                return self.write({'website_published': not self.website_published})
            else:
                raise AccessError(_("You don't have permission to modify the product template %s") % self.display_name)
        return super(ProductTemplate, self).website_publish_button()

    def _allow_redirect_to_apps_store(self):
        """
            Hook method for others to change redirect behavior.
            For example, one-time-payment app product may need to redirect users to apps store page
            while subscription app product may need to redirect users to subscription page.
        """
        self.ensure_one()
        return self.is_odoo_app
