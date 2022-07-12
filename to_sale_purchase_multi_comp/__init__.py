from . import models
from odoo import api, SUPERUSER_ID


def pre_init_hook(cr):
    env = api.Environment(cr, SUPERUSER_ID, {})

    products = env['product.template'].search([('service_to_purchase', '=', True)])
    for company in env['res.company'].search([]):
        vals_list = []
        for product in products:
            vals_list.append({
                'name': 'service_to_purchase',
                'fields_id': env.ref('sale_purchase.field_product_template__service_to_purchase').id,
                'res_id': 'product.template,%s' % product.id,
                'value_integer': 1,
                'company_id': company.id,
                'type': 'boolean'
                })
        if vals_list:
            env['ir.property'].sudo().with_context(force_company=company.id).create(vals_list)


def uninstall_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['ir.property'].sudo().search([
        ('name', '=', 'service_to_purchase'),
        ('fields_id', '=', env.ref('sale_purchase.field_product_template__service_to_purchase').id)
        ]).unlink()
