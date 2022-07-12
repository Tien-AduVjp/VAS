from odoo import api, SUPERUSER_ID

from . import models


def _replace_mobile_app_urls(env, action='post'):
    digest_mail_template = env.ref('digest.digest_mail_template', raise_if_not_found=False)
    if not digest_mail_template:
        return False

    odoo_google_play_url = 'https://play.google.com/store/apps/details?id=com.odoo.mobile'
    viindoo_google_play_url = 'https://play.google.com/store/apps/details?id=com.viindoo'
    odoo_app_store_url = 'https://itunes.apple.com/us/app/odoo/id1272543640'
    viindoo_app_store_url = 'https://itunes.apple.com/vn/app/viindoo-mobile/id1562267579'

    if action == 'post':
        digest_mail_template.body_html = digest_mail_template.body_html.replace(odoo_google_play_url, viindoo_google_play_url)
        digest_mail_template.body_html = digest_mail_template.body_html.replace(odoo_app_store_url, viindoo_app_store_url)
    else:
        digest_mail_template.body_html = digest_mail_template.body_html.replace(viindoo_google_play_url, odoo_google_play_url)
        digest_mail_template.body_html = digest_mail_template.body_html.replace(viindoo_app_store_url, odoo_app_store_url)


def uninstall_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _replace_mobile_app_urls(env, 'uninstall')
