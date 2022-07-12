def migrate(cr, version):
    # drop existing unique product_tmpl_id against Odoo module and replace with a Python constrainst.
    # It was too hard for debugging sql constraint
    cr.execute("""
    SELECT conname
    FROM pg_constraint
    WHERE conrelid = 'odoo_module'::regclass
      AND contype = 'u' and conname='odoo_module_product_tmpl_id_unique';
    """)
    if cr.fetchone():
        cr.execute("""
        ALTER TABLE odoo_module DROP CONSTRAINT odoo_module_product_tmpl_id_unique
        """)

