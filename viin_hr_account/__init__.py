# -*- coding: utf-8 -*-

from . import models

from odoo import api, SUPERUSER_ID


def _generate_department_analytic_account(env):
    env['hr.department'].sudo().with_context(active_test=False).search([])._generate_analytic_account()


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _generate_department_analytic_account(env)
