def migrate(cr, version):
    cr.execute("""
    ALTER TABLE odoo_module DROP CONSTRAINT IF EXISTS odoo_module_technical_name_unique;
    """
    )
