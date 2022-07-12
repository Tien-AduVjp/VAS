from werkzeug.exceptions import NotFound
from psycopg2.extensions import AsIs

from odoo import http, _
from odoo.http import request
from odoo.addons.website.controllers.main import QueryURL, Website
from odoo.addons.website_sale.controllers import main
from odoo.addons.http_routing.models.ir_http import slug


class Website(Website):

    @http.route(['/website/publish'])
    def publish(self, id, object):
        if object == 'odoo.module.version':
            omv = request.env[object].browse(id)
            omv.with_context(force=True).website_publish_button()
            return bool(omv.website_published)
        return super(Website, self).publish(id, object)


class WebsiteSale(main.WebsiteSale):

    def _prepare_product_values(self, product, category, search, **kwargs):
        val = super(WebsiteSale, self)._prepare_product_values(product, category, search, **kwargs)
        val["partner"] = request.env.user.partner_id
        val["product"] = product.sudo().with_context(partner=val["partner"])
        return val

    def _get_odoo_versions(self):
        OdooVersion = request.env['odoo.version']
        all_versions = OdooVersion.search([])
        return all_versions

    @http.route(['/apps/change_pricelist/<model("product.pricelist"):pl_id>',
                 '/apps/change_pricelist']
                , type='http', auth="public", website=True, sitemap=False)
    def apps_pricelist_change(self, pl_id=None, **post):
        if not request.website.dedicate_apps_store:
            return request.render("website.page_404")
        else:
            if not pl_id:
                return request.redirect(f"/apps/change_pricelist/{slug(request.env.user.partner_id.property_product_pricelist)}")
            if (pl_id.selectable or pl_id == request.env.user.partner_id.property_product_pricelist) \
                    and request.website.is_pricelist_available(pl_id.id):
                request.session['website_sale_current_pl'] = pl_id.id
                request.website.sale_get_order(force_pricelist=pl_id.id)
            return request.redirect(request.httprequest.referrer or '/apps')

    # main menu
    @http.route(['/apps'], type='http', auth="public", website=True, sitemap=True)
    def top_charts(self, **post):
        if not request.website.dedicate_apps_store:
            return request.render("website.page_404")
        else:
            category = request.env.ref('to_website_apps_store.prod_public_categ_modules')
            return self.category_top_charts(category, **post)

    # Apps menu
    @http.route(['/apps/modules'], type='http', auth="public", website=True, sitemap=False)
    def apps_top_charts(self, **post):
        if not request.website.dedicate_apps_store:
            return request.render("website.page_404")
        else:
            category = request.env.ref('to_website_apps_store.prod_public_categ_modules')
            return self.category_top_charts(category, **post)

    # Themes menu
    @http.route(['/apps/themes'], type='http', auth="public", website=True,  sitemap=True)
    def themes_top_charts(self, **post):
        if not request.website.dedicate_apps_store:
            return request.render("website.page_404")
        else:
            category = request.env.ref('to_website_apps_store.prod_public_categ_themes')
            return self.category_top_charts(category, **post)

    @http.route([
        '/apps/category/<model("product.public.category"):category>',
        '/apps/category',
        ], type='http', auth="public", website=True, sitemap=True)
    def category_top_charts(self, category=None, **post):
        if not request.website.dedicate_apps_store:
            return request.render("website.page_404")
        else:
            if not category:
                return request.redirect(f"/apps/category/{slug(request.env.ref('to_website_apps_store.prod_public_categ_odoo_apps'))}")
            pricelist = self._get_pricelist_context()[-1]
            request.session['website_sale_current_pl'] = pricelist.id
            if category in [
                request.env.ref('to_website_apps_store.prod_public_categ_odoo_apps'),
                request.env.ref('to_website_apps_store.prod_public_categ_themes'),
                request.env.ref('to_website_apps_store.prod_public_categ_modules'), ]:
                root_categ = category
            else:
                root_categ = category.parent_id

            keep = QueryURL('/apps/modules', category=category, pricelist=pricelist.id)
            request.context = dict(request.context, pricelist=pricelist.id, partner=request.env.user.partner_id)
            parent_category_ids = []
            values = {
                'list_url': '/apps/browse',
                'chart_url': '/apps',
                'pricelist': pricelist,
                'category': category,
                'root_categ': root_categ,
                'keep': keep,
                'parent_category_ids': parent_category_ids,
                'odoo_versions': self._get_odoo_versions(),
            }
            values.update(request.website._get_top_apps_charts(category=category))
            response = request.render("to_website_apps_store.apps", values)
            fav_categ_cookies = request.httprequest.cookies.get("fav_categ")
            if fav_categ_cookies:
                if category.name not in ["Apps", "Themes"]:
                    new_cookies = f"{fav_categ_cookies},{category.name}"
                    response.set_cookie("fav_categ", value=f"{new_cookies}".encode(), max_age=30 * 24 * 60 * 60)
            else:
                if category.name not in ["Apps", "Themes"]:
                    response.set_cookie("fav_categ", value=f"{category.name}".encode(), max_age=30 * 24 * 60 * 60)
            return response

    @http.route()
    def product(self, product, category='', search='', **kwargs):
        # TODO: in v15, please keep `if request.website.dedicate_apps_store and product._allow_redirect_to_apps_store():`
        # and change the behavior in `_allow_redirect_to_apps_store()`.
        # I.e. return `self.detailed_type == 'app'` instead of `self.is_odoo_app` as it is in v14.
        if request.website.dedicate_apps_store and product._allow_redirect_to_apps_store():
            odoo_module_versions = product.sudo().odoo_module_version_ids. \
                filtered(lambda omv:
                         omv.product_id.is_published and
                         omv.product_id.active and
                         omv.is_published and
                         omv.active)
            if not odoo_module_versions:
                return request.redirect('/apps', code=301)
            odoo_module_version = odoo_module_versions[0].sudo()
            return request.redirect('/apps/app/%s/%s' % (odoo_module_version.odoo_version_id.name, odoo_module_version.technical_name), code=301)
        return super(WebsiteSale, self).product(product, category, search, **kwargs)

    @http.route([
        '/apps/modules/browse',
        '/apps/modules/browse/<int:page>'
        ], type='http', auth="public", website=True, sitemap=False)
    def moduleapplist(self, page=0, search='', ppg=False, **post):
        if not request.website.dedicate_apps_store:
            return request.render("website.page_404")
        else:
            category = request.env.ref('to_website_apps_store.prod_public_categ_modules')
            return self.modulelist(page, category, search, ppg)

    @http.route([
        '/apps/themes/browse',
        '/apps/themes/browse/<int:page>'
        ], type='http', auth="public", website=True, sitemap=False)
    def modulethemelist(self, page=0, search='', ppg=False, **post):
        if not request.website.dedicate_apps_store:
            return request.render("website.page_404")
        else:
            category = request.env.ref('to_website_apps_store.prod_public_categ_themes')
            return self.modulelist(page, category, search, ppg)

    @http.route([
        '/apps/browse/category',
        '/apps/browse/category/<model("product.public.category"):category>',
        '/apps/browse/category/<model("product.public.category"):category>/page/<int:page>'
        ], type='http', auth="public", website=True, sitemap=True)
    def modulelist(self, page=0, category=None, search=None, ppg=False, **post):
        if not request.website.dedicate_apps_store:
            return request.render("website.page_404")
        else:
            if not category:
                return request.redirect(f"/apps/browse/category/{slug(request.env.ref('to_website_apps_store.prod_public_categ_odoo_apps'))}")
            pricelist = self._get_pricelist_context()[-1]
            request.session['website_sale_current_pl'] = pricelist.id
            if category in [
                request.env.ref('to_website_apps_store.prod_public_categ_odoo_apps'),
                request.env.ref('to_website_apps_store.prod_public_categ_themes'),
                request.env.ref('to_website_apps_store.prod_public_categ_modules')]:
                root_categ = category
            else:
                root_categ = category.parent_id
            if ppg:
                try:
                    ppg = int(ppg)
                except ValueError:
                    ppg = request.website.get_current_website().shop_ppg or 20
                post["ppg"] = ppg
            else:
                ppg = request.website.get_current_website().shop_ppg or 20

            if category:
                category = request.env['product.public.category'].search([('id', '=', int(category))], limit=1)
            if not category:
                raise NotFound()
            order = post.get('order')
            price = post.get('price')
            version = post.get('version')
            domain = request.website._sale_app_domain(search, category, price, version)
            keep = QueryURL('/apps/browse', category=category and int(category), search=search, order=order, price=price, version=version)

            user = request.env.user
            request.context = dict(request.context, pricelist=pricelist.id, partner=user.partner_id)

            values = {
                'list_url': '/apps/browse',
                'chart_url': '/apps',
                'search': search,
                'category': category,
                'main_object': category,
                'pricelist': pricelist,
                'root_categ': root_categ,
                'keep': keep,
                'odoo_versions': self._get_odoo_versions(),
            }

            url = "/apps/browse/category/%s" % slug(category)
            parent_category_ids = [category.id] if category else []
            current_category = category
            while current_category.parent_id:
                parent_category_ids.append(current_category.parent_id.id)
                current_category = current_category.parent_id
            values['parent_category_ids'] = parent_category_ids
            ModuleVersion = request.website._get_odoo_module_version_model()
            module_count = ModuleVersion.search_count(domain)
            module_order = order if order in ['price_currency desc', 'price_currency asc', 'name asc'] else None
            # ===================================================================================== #
            # we update keep.args into post to get category, search, order, price, version keywords #
            # later use those keywords for create new pager base on them.                           #
            # ===================================================================================== #
            post.update(keep.args)
            pager = request.website.pager(url=url, total=module_count, page=page, step=ppg, scope=7, url_args=post)
            module_versions = ModuleVersion.search(domain, limit=ppg, offset=pager['offset'], order=module_order)
            all_module_versions = ModuleVersion.search(domain)
            if order == 'Relevance':
                module_versions = category.get_top_odoo_modules(all_module_versions, version=version, price=price, limit=ppg, offset=pager['offset'])
            if order == 'Newest':
                module_versions = category.get_new_odoo_modules(all_module_versions, version=version, price=price, limit=ppg, offset=pager['offset'])
            if order == 'Downloads':
                module_versions = category.get_most_download_odoo_modules(all_module_versions, version=version, price=price, limit=ppg, offset=pager['offset'])
            if order == 'Purchases':
                module_versions = self._get_purchases_ids(all_module_versions, limit=ppg, offset=pager['offset'])
            if order == 'bestseller':
                module_versions = self._get_best_sell_ids(all_module_versions, limit=ppg, offset=pager['offset'])
            website_apps_sortable = [
                (_('Newest'), 'Newest'),
                (_('Downloads'), 'Downloads'),
                (_('Relevance'), 'Relevance'),
                (_('Purchases'), 'Purchases'),
                (_('Name'), 'name asc'),
                (_('Lowest Price'), 'price_currency asc'),
                (_('Highest Price'), 'price_currency desc'),
                (_('Best Sellers'), 'bestseller')
            ]
            values.update({
                'module_count': module_count,
                'pager': pager,
                'module_versions': module_versions.sudo().with_context(
                    partner=user.partner_id,
                    pricelist=pricelist.id,
                    exclude_standard_odoo_ee_module=True,
                    exclude_standard_odoo_ce_module=True
                    ),
                'website_apps_sortable': website_apps_sortable,
            })
            return request.render("to_website_apps_store.apps", values)

    @http.route(['/apps/upload'], type='http', auth='public', website=True, sitemap=False)
    def upload(self):
        # not yet developed
        if not request.website.dedicate_apps_store:
            pass
        return request.render("website.page_404")

    @http.route(['/apps/app/<string:odoo_version>/<string:technical_name>'], type='http', auth="public", website=True)
    def app(self, odoo_version, technical_name, search='', **kwargs):
        if not request.website.dedicate_apps_store:
            return request.render("website.page_404")
        else:
            user = request.env.user
            pricelist = self._get_pricelist_context()[-1]
            request.session['website_sale_current_pl'] = pricelist.id
            module = None

            # If odoo module is unpublished, you can't view detail page.
            # Pass `force_show=1` to the url, and boom, you can view it.
            force_show = kwargs.get('force_show', False)

            if odoo_version and technical_name:
                OdooModuleVersion = request.env['odoo.module.version']
                domain = [('technical_name', '=', technical_name), ('odoo_version_id.name', '=', odoo_version), ('git_branch_id.visible_on_apps_store', '=', True)]
                if not user.has_group('website.group_website_publisher'):
                    OdooModuleVersion = OdooModuleVersion.sudo()
                    if not force_show:
                        domain += [('is_published', '=', True)]
                module = OdooModuleVersion.search(domain)
            if not module:
                raise NotFound()
            module_context = dict(
                active_id=module.id,
                partner=user.partner_id,
                exclude_standard_odoo_ee_module=True,
                exclude_standard_odoo_ce_module=True,
                show_published_modules_only=(
                    not user.has_group('website.group_website_publisher') \
                    and not user.has_group('to_odoo_module.odoo_module_user')
                    and not force_show
                    ),
                )
            # ensure the right pricelist
            if not module_context.get('pricelist', False):
                module_context['pricelist'] = pricelist.id

            module = module.with_context(**module_context)

            category = module.public_categ_ids and module.public_categ_ids[0] or False

            keep = QueryURL('/apps/modules/browse', category=category and category.id, search=search, price='All')
            if module.public_categ_ids.parent_id == request.env.ref("to_website_apps_store.prod_public_categ_themes"):
                keep = QueryURL('/apps/themes/browse', category=category and category.id, search=search, price='All')

            values = {
                'pricelist': pricelist,
                'search': search,
                'category': category,
                'keep': keep,
                'url_app_keep': QueryURL('/apps/app'),
                'main_object': module,
                'additional_title': '%s - Odoo %s' % (module.name, module.odoo_version_id.name),
                'title': '%s - Odoo %s' % (module.name, module.odoo_version_id.name),
                'odoo_module': module,
                'odoo_versions': self._get_odoo_versions(),
                'user': user,
            }
            return request.render("to_website_apps_store.app", values)

    def _get_best_sell_ids(self, odoo_module_versions, limit, offset, date_range=30):
        # odoo_module_versions could be an empty recordset
        ModuleVersion = request.env['odoo.module.version']
        if not odoo_module_versions:
            return ModuleVersion
        sql = """
        WITH total_sale as(WITH currency_rate as (%s)
            SELECT
                mv.id AS mv_id,
                sol.price_total / COALESCE(cr.rate, 1.0) AS price_total_untaxed,
                s.date_order AS date
            FROM
                odoo_module_version as mv
                LEFT JOIN product_product pro ON (pro.odoo_module_version_id = mv.id)
                LEFT JOIN sale_order_line AS sol ON (sol.product_id = pro.id AND sol.state IN ('sale','done'))
                LEFT JOIN sale_order AS s ON (s.id = sol.order_id AND s.date_order > (SELECT (date_trunc('day', current_date) - interval '%s day')))
                LEFT JOIN product_pricelist pp ON (s.pricelist_id = pp.id)
                LEFT JOIN currency_rate cr ON (cr.currency_id = pp.currency_id AND
                cr.company_id = s.company_id AND
                cr.date_start <= COALESCE(s.date_order, now()) AND
                (cr.date_end IS NULL OR cr.date_end > COALESCE(s.date_order, now())))
            WHERE mv.id IN %s
        )
        SELECT mv_id,SUM(price_total_untaxed)
        FROM total_sale
        WHERE
            mv_id IS NOT NULL
        GROUP BY
            mv_id
        ORDER BY
            CASE WHEN SUM(price_total_untaxed) IS NULL
                THEN 1
                ELSE 0
                END,
            SUM(price_total_untaxed) DESC
        LIMIT %s
        OFFSET %s
        """
        request.env.cr.execute(
            sql,
            (
                AsIs(request.env['res.currency']._select_companies_rates()),
                date_range,
                tuple(odoo_module_versions.ids),
                limit,
                offset
                )
            )
        results = request.env.cr.dictfetchall()
        ids = []
        for oj in results:
            ids.append(oj['mv_id'])
        return ModuleVersion.browse(ids)

    def _get_purchases_ids(self, odoo_module_versions, limit, offset, date_range=30):
        # odoo_module_versions could be an empty recordset
        ModuleVersion = request.env['odoo.module.version']
        if not odoo_module_versions:
            return ModuleVersion
        sql = """
        WITH total_sale as(WITH currency_rate as (%s)
            SELECT
                mv.id AS mv_id,
                COUNT(sol.*) as sales_count
            FROM
                odoo_module_version as mv
                LEFT JOIN product_product pro ON (pro.odoo_module_version_id = mv.id)
                LEFT JOIN sale_order_line AS sol ON (sol.product_id = pro.id AND sol.state IN ('sale','done'))
                LEFT JOIN sale_order AS s ON (s.id = sol.order_id AND s.date_order > (SELECT (date_trunc('day', current_date) - interval '%s day')))
            WHERE mv.id IN %s
            GROUP BY mv.id
        )
        SELECT mv_id
        FROM total_sale
        WHERE
            mv_id IS NOT NULL
        GROUP BY
            mv_id
        ORDER BY
            CASE WHEN SUM(sales_count) IS NULL THEN 1 ELSE 0 END,
            SUM(sales_count) DESC
        LIMIT %s
        OFFSET %s
        """
        request.env.cr.execute(
            sql,
            (
                AsIs(request.env['res.currency']._select_companies_rates()),
                date_range,
                tuple(odoo_module_versions.ids),
                limit,
                offset
                )
            )
        results = request.env.cr.dictfetchall()
        ids = []
        for oj in results:
            ids.append(oj['mv_id'])
        return ModuleVersion.browse(ids)
