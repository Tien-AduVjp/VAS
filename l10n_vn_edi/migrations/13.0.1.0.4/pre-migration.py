
def migrate(cr, version):
    cr.execute("""
        ALTER TABLE account_journal ALTER COLUMN code TYPE character varying(6);
    """)

