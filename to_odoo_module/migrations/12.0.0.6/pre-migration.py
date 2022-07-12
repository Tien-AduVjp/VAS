def migrate(cr, version):
    cr.execute("""
    ALTER TABLE odoo_module_version DROP CONSTRAINT IF EXISTS odoo_module_version_vmodule_odoo_version_unique;
    ALTER TABLE odoo_module_version DROP CONSTRAINT IF EXISTS odoo_module_version_version_module_odoo_version_unique;
    """
    )
