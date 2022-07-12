def migrate(cr, version):
    # ============================================== #
    # - Create new column to table account_move_line #
    # - Fetch all relationship data                  #
    # - Update old data to new field                 #
    # - DROP OLD TABLE                               #
    # ============================================== #
    cr.execute("""
ALTER TABLE account_move_line ADD COLUMN odoo_module_version_id INTEGER;

UPDATE account_move_line
SET odoo_module_version_id = inv_omv_rel.odoo_module_version_id
FROM invoice_line_odoo_module_version_rel AS inv_omv_rel
WHERE account_move_line.id = inv_omv_rel.invoice_line_id;

DROP TABLE invoice_line_odoo_module_version_rel;
    """)
