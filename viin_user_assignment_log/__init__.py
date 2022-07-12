# -*- coding: utf-8 -*-

from odoo.models import Model
from odoo import api, SUPERUSER_ID

from . import models


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    to_precess_models = env['ir.model.fields'].search([
        ('name', 'in', ('user_id', 'invoice_user_id')),
        ('store', '=', True)
        ]).mapped('model_id').filtered(
            lambda m: isinstance(m, Model) \
                and not isinstance(m, env['user.assignment'].__class__)
                )
    vals_list = []
    for to_precess_model in to_precess_models:
        field_name = env[to_precess_model.model]._get_responsible_user_field_name()
        if not field_name:
            continue
        for record in env[to_precess_model.model].search([(field_name, '!=', False)]):
            vals = record._prepare_user_assignment_vals()
            if vals:
                vals_list.append(vals)
    if vals_list:
        env['user.assignment'].create(vals_list)


def uninstall_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    assignments = env['user.assignment'].search([])
    if assignments:
        assignments.unlink()
