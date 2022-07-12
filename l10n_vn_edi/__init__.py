from odoo import api, SUPERUSER_ID
from . import models
from . import wizard
from . import controllers

def _create_einvoice_services_vn_company(env):
    companies = env['res.company'].with_context(active_test=False).search([])
    if companies:
        companies._create_einvoice_services_vn_company()

def post_init_hook(cr, registry):
    cr.execute("""
        ALTER TABLE account_journal ALTER COLUMN code TYPE character varying(6);
    """)

    env = api.Environment(cr, SUPERUSER_ID, {})
    _create_einvoice_services_vn_company(env)
