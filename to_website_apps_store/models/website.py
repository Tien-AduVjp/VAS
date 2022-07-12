from odoo import models, fields


class Website(models.Model):
    _inherit = 'website'

    dedicate_apps_store = fields.Boolean(string='Dedicated Apps Store', default=True,
                                            help="If checked, all products that are Odoo Apps will NOT be listed on your website's Shop. Instead, a"
                                            " dedicted Apps Store will be activated on your website, beside your Shop.")

    def sale_product_domain(self):
        domain = super(Website, self).sale_product_domain()
        if self.dedicate_apps_store:
            domain += [('is_odoo_app', '=', False)]
        return domain

    def _get_odoo_module_version_model(self):
        OdooModuleVersion = self.env['odoo.module.version']
        if not self.env.user.has_group('website.group_website_publisher') and not self.env.user.has_group('to_odoo_module.odoo_module_user'):
            return OdooModuleVersion.sudo().with_context(show_published_modules_only=True)
        return OdooModuleVersion

    def _sale_app_domain(self, search=None, category_id=None, price=None, version=None):
        domain = [
            # we will not show module versions that have no product associated
            ('product_id', '!=', False),
            # we will not show module versions the products of which are not sale_ok
            ('product_id.sale_ok', '=', True),
            # we will NOT show the standard Odoo modules
            ('is_standard_odoo_module', '=', False),
            # we won't show modules from branches which marked not visible on apps store
            ('git_branch_id.visible_on_apps_store', '=', True),

            '|', ('module_id.website_ids', 'in', [self.id]), ('module_id.website_ids', '=', False)]

        if not self.env.user.has_group('website.group_website_publisher') or self._context.get('show_published_modules_only', False):
            domain += [('is_published', '=', True)]

        if category_id:
            domain += [('public_categ_ids', 'child_of', int(category_id))]
        if price == 'Free':
            domain += [('price_currency', '=', 0)]
        if price == 'Paid':
            domain += [('price_currency', '!=', 0)]
        if version:
            domain += [('odoo_version_id.name', '=', version)]
        else:
            # we will show the latest version only
            domain += [('is_latest_website_published_version', '=', True)]

        if search:
            domain += ['|', '|', ('technical_name', 'ilike', search), ('name', 'ilike', search)]
            for srch in search.split(" "):
                domain += [
                    '|', '|', ('name', 'ilike', '%' + srch + '%'), ('summary', 'ilike', '%' + srch + '%'),
                    ('description', 'ilike', '%' + srch + '%')]
        return domain

    def _get_top_rated_apps(self, search=None, category=None, price=None, version=None, limit=4, offset=0):
        domain = self._sale_app_domain(search, category, price, version)
        return self._get_odoo_module_version_model().search(domain, offset=offset, limit=limit, order='website_published_date desc, full_version_str desc, id desc')

    def _get_new_apps(self, search=None, category=None, price=None, version=None, limit=4, offset=0):
        domain = self._sale_app_domain(search, category, price, version)
        return self._get_odoo_module_version_model().search(domain, offset=offset, limit=limit, order='website_published_date desc, full_version_str desc, id desc')

    def _get_most_downloaded_apps(self, search=None, category=None, price=None, version=None, limit=4, offset=0):
        domain = self._sale_app_domain(search, category, price, version)
        return self._get_odoo_module_version_model().search(domain, offset=offset, limit=limit, order='external_downloads_count desc')

    def _get_best_sold_odoo_modules_apps(self, search=None, category=None, price=None, version=None, limit=4, offset=0):
        domain = self._sale_app_domain(search, category, price, version)
        return self._get_odoo_module_version_model().search(domain, offset=offset, limit=limit, order='website_published_date desc, full_version_str desc, id desc')

    def _get_top_apps_charts(self, category=None, limit=4, offset=0):
        return {
            'top_ids': self._get_top_rated_apps(category=category, limit=limit, offset=offset),
            'new_ids': self._get_new_apps(category=category, limit=limit, offset=offset),
            'most_download_ids': self._get_most_downloaded_apps(category=category, limit=limit, offset=offset),
            'top_charts': 1
            }
