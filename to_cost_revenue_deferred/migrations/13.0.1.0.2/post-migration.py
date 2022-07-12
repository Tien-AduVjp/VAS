# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID
from odoo.tools import float_compare


def _fix_company_rule(env):
    rule = env.ref('to_cost_revenue_deferred.cost_revenue_deferral_category_multi_company_rule', raise_if_not_found=False)
    if rule:
        rule.write({'domain_force': "['|',('company_id','=',False),('company_id','in',company_ids)]"})


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    _fix_company_rule(env)

