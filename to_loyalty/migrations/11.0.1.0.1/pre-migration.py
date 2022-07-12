from odoo import api, SUPERUSER_ID


def _create_fields(cr):
    sql = ""
    cr.execute("""
    SELECT column_name
    FROM information_schema.columns
    WHERE table_name='loyalty_point' and column_name='manual_adjustment';
    """)
    if not cr.fetchone():
        sql += """
        ALTER TABLE loyalty_point ADD COLUMN manual_adjustment boolean DEFAULT True;
        UPDATE loyalty_point SET manual_adjustment=False WHERE product_id IS NOT NULL;
        """

    if sql:
        cr.execute(sql)


def migrate(cr, version):
    _create_fields(cr)
