from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    """
    Fix errors when scan branch after rename module.
    """

    env = api.Environment(cr, SUPERUSER_ID, {})
    odoo_modules_versions = env['odoo.module.version'].with_context(active_test=False).search([('product_tmpl_id', '!=', False)])
    odoo_modules_versions.read(['product_tmpl_id', 'odoo_version_id'])
    odoo_modules_versions.odoo_version_id.read(['product_attribute_value_id'])

    products_tmpl = odoo_modules_versions.mapped('product_tmpl_id')

    odoo_version_attribute_lines = env['product.template.attribute.line'].search([
        ('product_tmpl_id', 'in', products_tmpl.ids),
        ('attribute_id', '=', env.ref('to_product_odoo_version.product_attribute_odoo_version').id)
    ])
    odoo_version_attribute_lines.read(['product_tmpl_id', 'value_ids'])

    for product_tmpl in products_tmpl:
        omv_product_attribute_values = odoo_modules_versions.filtered(
            lambda att_val: att_val.product_tmpl_id.id == product_tmpl.id
        ).odoo_version_id.product_attribute_value_id
        odoo_version_attribute_line = odoo_version_attribute_lines.filtered(
            lambda att_val: att_val.product_tmpl_id.id == product_tmpl.id
        )

        if odoo_version_attribute_line:
            product_tmpl_product_attribute_values = odoo_version_attribute_line.value_ids
            missing_attribute_values = omv_product_attribute_values - product_tmpl_product_attribute_values
            if missing_attribute_values:
                product_tmpl.with_context(tracking_disable=True).write({
                    'attribute_line_ids': [(1, odoo_version_attribute_line.id, {
                        'value_ids': [(4, attribute_value.id) for attribute_value in missing_attribute_values]
                    })]
                })
