from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    sql = ""
    cr.execute("""
    SELECT column_name
    FROM information_schema.columns
    WHERE table_name='vehicle_class' and column_name='legacy_type';
    """)
    if not cr.fetchone():
        sql += """
        ALTER TABLE vehicle_class ADD COLUMN legacy_type character varying;
        UPDATE vehicle_class SET legacy_type = type;
        """

    if sql:
        cr.execute(sql)

