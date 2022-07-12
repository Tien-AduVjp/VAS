import math

from odoo import models, fields, api, _
from odoo.http import request
from odoo.exceptions import AccessError


class OdooModuleVersion(models.Model):
    _name = 'odoo.module.version'
    _inherit = ['odoo.module.version', 'website.published.multi.mixin', 'website.seo.metadata', 'rating.mixin']
    
    @api.model
    def _default_public_category_ids(self):
        return [(4, self.env.ref("to_website_apps_store.prod_public_categ_modules").id)]

    public_categ_ids = fields.Many2many('product.public.category', 'odoo_module_version_prod_public_categ_rel', 'odoo_module_version_id', 'public_categ_id',
                                        string='Website Categories', default=_default_public_category_ids)
    website_intro = fields.Html('Website Intro HTML')
    replace_product_website_description = fields.Boolean(default=True, string='Replace Product Website Description', help="If enabled,"
                                                       " the description of this module will be used on website instead of the website"
                                                       " description of the corresponding product.\n"
                                                       " Note, if you edit the product's description, this field will be set as disabled"
                                                       " automatically.")
    website_published_date = fields.Datetime(string='Website Published Date', readonly=True,
                                             help="The value of this field is updated upon the first published only.")

    anchor_title = fields.Char(string='Anchor Title', compute='_compute_anchor_title', help="Technical field for usage with anchor"
                               " tag's title attribute.")
    is_latest_website_published_version = fields.Boolean(string='Is Latest Website Published Version', compute='_compute_is_latest_website_published_version',
                                                       store=True, help="This is to indicate that this version the the latest version of the respective"
                                                       " module that has been published on the website")

    def write(self, vals):
        # ensure we do not override website_published_date if it is already set.
        if 'website_published_date' in vals and vals['website_published_date'] and not self._context.get('ignore_website_published_date_test'):

            # update website_published_date for the module versions that have no website_published_date set.
            to_update_website_published_date = self.filtered(lambda omv: not omv.website_published_date)
            to_update_website_published_date.with_context(
                ignore_website_published_date_test=True
                ).write(vals)

            # remove website_published_date from vals then write the remaining
            vals.pop('website_published_date')
            (self - to_update_website_published_date).write(vals)
            return True
        else:
            return super(OdooModuleVersion, self).write(vals)

    @api.depends('module_id.latest_website_published_version_id')
    def _compute_is_latest_website_published_version(self):
        for r in self:
            r.is_latest_website_published_version = (r.website_published and r == r.module_id.latest_website_published_version_id)

    def _compute_anchor_title(self):
        self.read(['name', 'odoo_version_id'])
        for r in self:
            r.anchor_title = _("%s for Odoo %s") % (r.name, r.odoo_version_id.name)

    def _update_website_published_date(self):
        self.filtered(lambda mv: mv.is_published and not mv.website_published_date).write({'website_published_date': fields.Datetime.now()})
        self.filtered(lambda mv: not mv.is_published and mv.website_published_date).write({'website_published_date': False})

    def _website_publish_products(self):
        """
        This method ensures:
            1. If all Odoo module versions of a product template is unpublished, the product template is published too.
            2. If at least one Odoo module version of a product template is published, the product template is published too.
        """
        related_prod_tmps = self.mapped('product_id.product_tmpl_id')
        related_module_versions = self.search([('product_id.product_tmpl_id', 'in', related_prod_tmps.ids)])
        to_publish = self.env['product.template']
        to_unpublish = self.env['product.template']
        for product_template in related_prod_tmps:
            related_odoo_module_versions = related_module_versions.filtered(lambda mv: mv.product_id.product_tmpl_id == product_template)
            if any(omv.is_published for omv in related_odoo_module_versions):
                if not product_template.website_published:
                    to_publish |= product_template
            else:
                if product_template.website_published:
                    to_unpublish |= product_template
            
        for product_template in (to_publish + to_unpublish):
            product_template.with_context(force=True).website_publish_button()

    def website_publish_button(self):
        if self._context.get("force", False):
            self.ensure_one()
            if self.env.user.has_group('website.group_website_publisher'):
                self.write({'website_published': not self.website_published})
                self._update_website_published_date()
                self._website_publish_products()
                return bool(self.website_published)
            else:
                raise AccessError(_("You don't have permission to modify the Odoo module version %s")
                                  % self.display_name)
        else:
            res = super(OdooModuleVersion, self).website_publish_button()
            # update the website_published_date
            self._update_website_published_date()
            # apply the published to the corresponding products. The products then do the same thing for their template accordingly
            self._website_publish_products()
            return res

    def _get_query_for_other_versions(self):
        sql = super(OdooModuleVersion, self)._get_query_for_other_versions()
        if self._context.get('show_published_modules_only', False):
            sql += """
                AND a.is_published = True
            """
        return sql

    @api.depends('index_html', 'description')
    def _get_desc(self):
        for r in self:
            if r.replace_product_website_description == True:
                super(OdooModuleVersion, r)._get_desc()
            else:
                r.description_html = r.product_id.product_tmpl_id.website_description

    def _compute_website_url(self):
        for omv in self:
            omv.website_url = '/apps/app/%s/%s' % (omv.odoo_version_id.name, omv.technical_name)

    def get_website_rating(self):
        rating = self.rating_get_stats([('website_published', '=', True)])
        full = math.floor(rating['avg']/2)
        half = math.ceil(rating['avg']/2) - full
        empty = 5 - half - full
        return {'full': full, 'half': half, 'empty': empty, 'total': rating['total'], 'avg': rating['avg']}
    
    def _get_website_common_search_domain(self, search=None, category=None, price=None, version=None):
        domain = [("is_published", "=", True), ("website_published_date", "!=", False)]
        if search:
            domain += [("id", "in", list(map(int, search)))]
        if category:
            domain += [("public_categ_ids", "child_of", int(category))]
        if version:
            domain += [('odoo_version_id.name', '=', version)]
        if price:
            if price == "Free":
                domain += [("price_currency", "=", 0)]
            else:
                domain += [("price_currency", "!=", 0)]
        return domain

    def get_most_downloaded(self, search, category, price, version, limit, offset):
        domain = self._get_website_common_search_domain(search, category, price, version)
        return self.sudo().search(domain, limit=limit, offset=offset, order='external_downloads_count desc')
    
    def get_new(self, search, category, price, version, limit, offset):
        domain = self._get_website_common_search_domain(search, category, price, version)
        return self.sudo().search(domain, limit=limit, offset=offset, order='website_published_date desc')
    
    def get_top_rated(self, search, category, price, version, limit, offset):
        # split, sort search_querry & fav_categ by view & search frequency
        search_querry = request.httprequest.cookies.get("search_querry")
        if search_querry:
            search_querry = search_querry.split(",")
            querries = {}
            for q in search_querry:
                querries[q] = querries.get(q, 0) + 1
            querries = sorted(querries, key=lambda x: querries[x], reverse=True)

        fav_categ = request.httprequest.cookies.get("fav_categ")
        categs = {}
        if fav_categ:
            fav_categ = fav_categ.split(",")
            for categ in fav_categ:
                categs[categ] = categs.get(categ, 0) + 1
            categs = sorted(categs, key=lambda x: categs[x], reverse=True)
        # sorted by fav_categ
        categs = list(categs)
        domain = self._get_website_common_search_domain(search, category, price, version)
        odoo_module_versions = self.sudo().search(domain, limit=limit, offset=offset)
        for app in odoo_module_versions:
            if app.public_categ_ids.name not in categs:
                categs.append(app.public_categ_ids.name)
        return odoo_module_versions.sorted(key=lambda x: categs.index(x.public_categ_ids.name))

    def _prepare_product_update_data(self):
        update_data = super(OdooModuleVersion, self)._prepare_product_update_data()
        product_variant_images = {img.id: img.image_1920 for img in self.product_id.product_variant_image_ids}
        omv_images = {img.id: (img.name, img.image) for img in self.image_ids}
        if product_variant_images or omv_images:
            update_data['product_variant_image_ids'] = []
        for image in omv_images.keys():
            keep = None
            for product_image in product_variant_images.keys():
                if self.module_id._identical_images(omv_images[image][1], product_variant_images[product_image]):
                    keep = product_image
                    break
            if not keep:
                update_data['product_variant_image_ids'] += [(0, 0, {'name': omv_images[image][0],
                                                                     'image_1920': omv_images[image][1]})]
            else:
                product_variant_images.pop(keep)
        if product_variant_images:
            update_data['product_variant_image_ids'] += [(2, image_id) for image_id in product_variant_images.keys()]
        return update_data

    def _default_website_meta(self):
        res = super(OdooModuleVersion, self)._default_website_meta()
        res['default_opengraph']['og:image'] = res['default_twitter']['twitter:image'] = self.env['website'].image_url(self, 'image_1024')
        return res
