from odoo import api, SUPERUSER_ID, _
from odoo.exceptions import UserError

from . import models
from . import wizard
from . import report


def _ensure_no_account_asset_installed(env):
    """
    This method ensures the Odoo EE's account_asset module is not installed before installing this to_account_asset
    """
    account_asset_module = env['ir.module.module'].search([
        ('name', '=', 'account_asset'),
        ('state', '=', 'installed')
        ], limit=1)
    if account_asset_module:
        to_account_asset_module = env['ir.module.module'].search([('name', '=', 'to_account_asset')], limit=1)
        raise UserError(_("You must uninstall the module %s (%s) before you could install the module %s (%s).")
                        % (
                            account_asset_module.shortdesc,
                            account_asset_module.name,
                            to_account_asset_module.shortdesc,
                            to_account_asset_module.name
                            )
                        )


def pre_init_hook(cr):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _ensure_no_account_asset_installed(env)


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    companies = env['res.company'].search([('chart_template_id', '!=', False)])
    if companies:
        companies._generate_asset_journal()

