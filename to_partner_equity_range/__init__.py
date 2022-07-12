from . import models


def _pre_init_to_partner_equity_range(cr):
    """Pre-populate stored computed/related fields to speedup installation"""

    cr.execute("""
    SELECT column_name
    FROM information_schema.columns
    WHERE table_name='res_partner' and column_name='equity_range_id';
    """)
    if not cr.fetchone():
        cr.execute("""
        ALTER TABLE res_partner ADD COLUMN equity_range_id integer;
        UPDATE res_partner SET equity_range_id = NULL;
        """)
