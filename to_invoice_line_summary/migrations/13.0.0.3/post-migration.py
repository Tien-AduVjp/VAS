def migrate(cr, version):
    cr.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name='account_move' AND column_name='invoice_display_mode';
    """)
    if cr.fetchone():
        cr.execute("""
            UPDATE account_move
            SET invoice_display_mode = CASE invoice_display_mode
            WHEN 'details' THEN 'invoice_lines'
            WHEN 'invoice_line_summary' THEN 'invoice_line_summary_lines'
            ELSE 'invoice_lines'
            END;
            UPDATE account_journal
            SET invoice_display_mode = CASE invoice_display_mode
            WHEN 'details' THEN 'invoice_lines'
            WHEN 'invoice_line_summary' THEN 'invoice_line_summary_lines'
            ELSE 'invoice_lines'
            END;
        """)
