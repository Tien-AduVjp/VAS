from odoo import models, api, fields
from collections import Counter

BLACKLISTED_KEYWORDS = [
    '*',
    '-',
    '+',
    '/',
    '',
    ',',
    '.',
    '_',
    ';',
    '~',
    '^',
    '`',
    'i',
    'you',
    'we',
    'them',
    'they',
    'is',
    'with',
    'from',
    'the',
    'that',
    'all',
    'multiple',
    'to',
    'into',
    'at',
    'in',
    'on',
    'there',
    ]
# this dict is used for mapping odoo module versions against public categories during odoo module version discovery with git fetching
PUBLIC_CATEG_MAP = {
    'modules': {
        'accounting': 'to_website_apps_store.prod_public_categ_accounting',
        'discuss': 'to_website_apps_store.prod_public_categ_discuss',
        'document management': 'to_website_apps_store.prod_public_categ_document_management',
        'ecommerce': 'to_website_apps_store.prod_public_categ_ecommerce',
        'human resources': 'to_website_apps_store.prod_public_categ_human_resources',
        'industries': 'to_website_apps_store.prod_public_categ_industries',
        'localization': 'to_website_apps_store.prod_public_categ_localization',
        'manufacturing': 'to_website_apps_store.prod_public_categ_manufacturing',
        'marketing': 'to_website_apps_store.prod_public_categ_marketing',
        'point of sale': 'to_website_apps_store.prod_public_categ_point_of_sale',
        'productivity': 'to_website_apps_store.prod_public_categ_productivity',
        'project': 'to_website_apps_store.prod_public_categ_project',
        'purchases': 'to_website_apps_store.prod_public_categ_purchases',
        'sales': 'to_website_apps_store.prod_public_categ_sales',
        'warehouse': 'to_website_apps_store.prod_public_categ_warehouse',
        'website': 'to_website_apps_store.prod_public_categ_website',
        'fleet': 'to_website_apps_store.prod_public_categ_fleet',
        'extra tools': 'to_website_apps_store.prod_public_categ_extra_tools',
        },
    'themes': {
        'backend': 'to_website_apps_store.prod_public_categ_themes_backend',
        'corporate': 'to_website_apps_store.prod_public_categ_themes_corporate',
        'creative': 'to_website_apps_store.prod_public_categ_themes_creative',
        'ecommerce': 'to_website_apps_store.prod_public_categ_themes_ecommerce',
        'education': 'to_website_apps_store.prod_public_categ_themes_education',
        'entertainment': 'to_website_apps_store.prod_public_categ_themes_entertainment',
        'nonprofit': 'to_website_apps_store.prod_public_categ_themes_nonprofit',
        'personal': 'to_website_apps_store.prod_public_categ_themes_personal',
        'retail': 'to_website_apps_store.prod_public_categ_themes_retail',
        'services': 'to_website_apps_store.prod_public_categ_themes_services',
        'technology': 'to_website_apps_store.prod_public_categ_themes_technology',
        'miscellaneous': 'to_website_apps_store.prod_public_categ_themes_miscellaneous',
        }
    }


class GitBranch(models.Model):
    _inherit = 'git.branch'

    apps_website_published = fields.Boolean(string='Apps Published', default=False, tracking=True,
                                            help="If enabled, all the Odoo apps in this branch will be published on the website by default")
    visible_on_apps_store = fields.Boolean(string='Visible on Apps Store', default=True, tracking=True,
                                           help="If enabled, all the Odoo apps in this branch will be shown on Apps Store for online selling.\n"
                                                "If for any reason, you only wanted to publishing odoo module version without online selling "
                                                "lifetime version of it,\nyou could change this option.")

    @api.model
    def _parse_manifest(self, manifest_file_name):
        vals = super(GitBranch, self)._parse_manifest(manifest_file_name)

        if vals.get('category', False):
            # split categories by '/'
            categs = [it.strip() for it in vals['category'].split('/')]

            # if the first category like theme, the module is a theme
            if len(categs) > 1 and categs[0].lower() in ('theme', 'themes'):
                k = PUBLIC_CATEG_MAP['themes']
                del categs[0]
            else:
                k = PUBLIC_CATEG_MAP['modules']

            categ = categs[-1]
            try:
                xml_id = k[categ.lower()]
            except KeyError:
                xml_id = k['miscellaneous'] if k == PUBLIC_CATEG_MAP['themes'] else k['extra tools']

            categ_id = self.env.ref(xml_id, raise_if_not_found=False)
            if categ_id:
                vals['public_categ_ids'] = [(6, 0, [categ_id.id])]
            else:
                vals['public_categ_ids'] = [(6, 0, [])]

        # There is a chance vals could be an empty dict
        # then we need to check that for each and every key we want to implement below
        module_text = []
        if 'name' in vals:
            vals['website_meta_title'] = vals['name']
            module_text.append(vals['name'])
        if 'summary' in vals:
            vals['website_meta_description'] = vals['summary']
            module_text.append(vals['summary'])
        if 'description' in vals:
            module_text.append(vals['description'])

        if module_text:
            kw_list = self.get_most_common_keywords(" ".join(module_text))
            if kw_list:
                vals['website_meta_keywords'] = ','.join(kw_list)
            else:
                vals['website_meta_keywords'] = False
            
        if self.apps_website_published and vals.get('installable', False) and vals.get('category', '') and vals.get('category', '') != 'Hidden':
            vals.update({
                'is_published': True,
                'website_published_date': fields.Datetime.now()
                })
        else:
            vals.update({
                'is_published': False,
                })

        return vals

    def get_most_common_keywords(self, plain_text, occurrence=3, max_keywords=10):
        kw_list = []
        for item in Counter(plain_text.split()).most_common():
            if item[0] not in BLACKLISTED_KEYWORDS and item[1] >= occurrence:
                kw_list.append(item)
        # sorted ascending
        sorted_by_occurrence = sorted(kw_list, key=lambda kv: kv[1])
        # get the last max_keywords elements
        kw_list = sorted_by_occurrence[-max_keywords:]

        return list(dict(kw_list).keys())

    def _discover_odoo_modules(self):
        odoo_module_versions = super(GitBranch, self)._discover_odoo_modules()

        # synchronize public categories from Odoo Module Versions into product templates
        product_tmpl_ids = odoo_module_versions.mapped('product_tmpl_id')
        for product_tmpl_id in product_tmpl_ids:
            # overriding product template's category with the corresponding odoo module versions' categories
            product_tmpl_id.write({
                'public_categ_ids': [(6, 0, product_tmpl_id.odoo_module_version_ids.mapped('public_categ_ids').ids)]
                })
        return odoo_module_versions
    
    def action_discover_odoo_modules(self):
        odoo_module_versions = super(GitBranch, self).action_discover_odoo_modules()
        odoo_module_versions._update_website_published_date()
        odoo_module_versions._website_publish_products()
        return odoo_module_versions

