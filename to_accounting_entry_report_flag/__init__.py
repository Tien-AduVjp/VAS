from . import models


def pre_init_hook(cr):
    """
    The field `legal_report_off` of the model 'account.move.line' is a stored and computed field.
    This function, upon installation of this module, will Pre-populate the field to avoid unneccessary computation
    to speedup installation on database with a lots of records in account.move.line. For example, installing this
    module on a database of 650 thousand account.move.line records may takes more than 10 minutes    
    """
    sql = ""

    cr.execute("""
    SELECT column_name
    FROM information_schema.columns
    WHERE table_name='account_move_line' and column_name='legal_report_off';
    """)
    if not cr.fetchone():
        sql += """
        ALTER TABLE account_move_line ADD COLUMN legal_report_off boolean DEFAULT false;
        """

    if sql:
        cr.execute(sql)