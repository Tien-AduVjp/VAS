from odoo import models, fields, api


class OdooModule(models.Model):
    _name = 'odoo.module'
    _inherit = ['odoo.module', 'website.published.mixin', 'rating.mixin']
    _mail_post_access = 'read'

    website_ids = fields.Many2many('website', string='Websites', help="This is to restrict publishing to these given websites")
    latest_website_published_version_id = fields.Many2many('odoo.module.version', string='Latest Website Published Version',
                                                           compute='_compute_latest_website_published_version', store=True,
                                                           index=True, help="This field is to indicated the latest version that"
                                                           " has been published on website")

    @api.depends('odoo_module_version_ids', 'odoo_module_version_ids.is_published')
    def _compute_latest_website_published_version(self):
        for r in self:
            # candidate must have full_version_str to ensure both version and Odoo version have been input
            # this is to avoid error when calling this on the context of onchange where either of version or Odoo version have not been filled
            candidates = r.odoo_module_version_ids.filtered(lambda v: v.full_version_str and v.is_published)
            if candidates:
                # sort the record by full_version_str descending
                # Hint: list(map(int, v.full_version_str.split('.')) will return a list like [12, 0, 6, 2, 1] presenting '12.0.6.2.1'
                r.latest_website_published_version_id = candidates.sorted(key=lambda v: list(map(int, v.full_version_str.split('.'))), reverse=True)[0]
            else:
                r.latest_website_published_version_id = False

    def _prepare_product_tmpl_update_data(self):
        update_data = super(OdooModule, self)._prepare_product_tmpl_update_data()

        product_template_images = {img.id: img.image_1920 for img in self.product_tmpl_id.product_template_image_ids}
        latest_published_omv_images = {img.id: (img.name, img.image) for img in self.latest_website_published_version_id.image_ids}
        if product_template_images or latest_published_omv_images:
            update_data['product_template_image_ids'] = []
        for image in latest_published_omv_images.keys():
            keep = None
            for pt_image in product_template_images.keys():
                if self._identical_images(latest_published_omv_images[image][1], product_template_images[pt_image]):
                    keep = pt_image
                    break
            if not keep:
                update_data['product_template_image_ids'] += [(0, 0, {'name': latest_published_omv_images[image][0],
                                                                      'image_1920': latest_published_omv_images[image][1]})]
            else:
                product_template_images.pop(keep)
        if product_template_images:
            update_data['product_template_image_ids'] += [(2, image_id) for image_id in product_template_images.keys()]
        return update_data
