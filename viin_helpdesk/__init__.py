from . import controllers
from . import models
from . import reports

from odoo import api, SUPERUSER_ID, _
from odoo.exceptions import UserError


def _activate_digest(env):
    default_digest = env.ref('digest.digest_digest_default')
    default_digest.write({
        'kpi_helpdesk_ticket_opened': True,
        'kpi_helpdesk_ticket_closed': True,
        })


def _ensure_no_helpdesk_installed(env):
    """
    This method ensures the Odoo EE's helpdesk module is not installed before installing this viin_helpdesk
    """
    helpdesk_module = env['ir.module.module'].search([
        ('name', '=', 'helpdesk'),
        ('state', '=', 'installed')
        ], limit=1)
    if helpdesk_module:
        viin_helpdesk_module = env['ir.module.module'].search([('name', '=', 'viin_helpdesk')], limit=1)
        raise UserError(_("You must uninstall the module %s (%s) before you could install the module %s (%s).")
                        % (
                            helpdesk_module.shortdesc,
                            helpdesk_module.name,
                            viin_helpdesk_module.shortdesc,
                            viin_helpdesk_module.name
                            )
                        )


def pre_init_hook(cr):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _ensure_no_helpdesk_installed(env)


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _activate_digest(env)
    companies = env['res.company'].search([('default_helpdesk_team_id', '=', False)])
    companies._create_helpdesk_team_if_not_exits()
