# -*- coding: utf-8 -*-

from . import models
from . import report

from odoo import api, SUPERUSER_ID, _


def _set_overtime_base_advantages(env):
    env['hr.advantage.template'].search([]).write({
        'overtime_base_factor': True
        })


def _generate_payroll_rules(env):
    env['res.company'].search([])._generate_payroll_rules()


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _set_overtime_base_advantages(env)
    _generate_payroll_rules(env)
