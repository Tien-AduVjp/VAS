def migrate(cr, version):
    sql = """
    UPDATE res_company
    SET use_employee_advance_pass_through_account = TRUE;
    """
    cr.execute(sql)
