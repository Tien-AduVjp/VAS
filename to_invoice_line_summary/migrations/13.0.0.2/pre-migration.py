def migrate(cr, version):
    cr.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name='account_move' AND column_name='invoice_display_mode';
    """)
    if not cr.fetchone():
        cr.execute("""
            ALTER TABLE account_move
            ADD COLUMN invoice_display_mode varchar;
            COMMENT ON COLUMN account_move.invoice_display_mode IS 'Invoice Display Mode';
            UPDATE account_move
            SET invoice_display_mode = 'details';
        """)