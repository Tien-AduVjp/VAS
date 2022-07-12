def migrate(cr, version):
    sql = ""

    cr.execute("""
    SELECT column_name
    FROM information_schema.columns
    WHERE table_name='employee_advance' and column_name='company_id';
    """)
    if not cr.fetchone():
        sql += """
        ALTER TABLE employee_advance ADD COLUMN company_id integer;
        """
        sql += """
        UPDATE employee_advance AS adv
        SET company_id = aj.company_id
        FROM account_journal AS aj
        WHERE aj.id = adv.journal_id;
        """

    if sql:
        cr.execute(sql)
